# Grant Options Income System

A rules-based daily decision pipeline for selling option premium on indices
and defensive equities. This document is written to be read by humans and by
AI advisors (Chat, Claude, ChatGPT) who need to understand the full system
before commenting on trade decisions or proposing changes.

Last updated: Phase 1.5 (May 2026).

---

## What This Is

The system takes in live market data, decides whether today is a trade day,
screens a configured universe of tickers for trade candidates, constructs
specific spread proposals, validates them in real time before entry, and
outputs trade instructions formatted for manual Robinhood entry.

The system is the analytical engine. The human (Brendan) does the actual
clicking. There is no broker API integration yet. That is a deliberate
Phase 1 choice.

## The 5-Stage Pipeline

Every trade decision flows through these stages in order. Each stage can gate
the next. If a candidate fails any stage, the system does not propose it.

1. **Regime Engine.** Classifies the day into one of 7 regimes. If the regime
   is closed (NO-TRADE), the pipeline halts at this stage and surfaces
   nothing.
2. **Scanner.** Screens each ticker in the universe against IV, liquidity,
   dollar volume, and compression filters. Returns ranked candidates.
3. **Trade Builder.** For each surviving candidate, constructs bull-put
   spreads, bear-call spreads, and iron condors at every expiration in the
   14-21 DTE window. Computes credit, POP, both M2M-style risk levels,
   resilience score, exit ladder. Ranks proposals.
4. **Validator.** Right before manual entry, refetches the chain and
   re-checks regime, credit drift, IV ceiling, M2M proximity, and gamma
   window. Returns VALID or INVALID with reasoning.
5. **Execution.** Renders a Robinhood-friendly trade card with per-leg
   action, strike, expiry, limit price suggestion, exit targets, and stops.

## Regime Engine

The regime is the daily gate. The classifier looks at VIX bands, SPX trend,
breakout detection, and Bollinger-band compression, then maps the state to
one of seven labels. Each label maps to a deploy decision and a size
multiplier.

The 7 regimes and their default behavior:

| Regime | Deploy? | Size mult | Description |
|---|---|---|---|
| BENIGN_TREND | Yes | 1.0 | SPX above slow SMA, normal VIX |
| BENIGN_CHOP | Yes | 1.0 | SPX below slow SMA but no breakdown, normal VIX |
| COMPRESSION | Yes | 1.0 | BB width well below average. Favors iron condors |
| ELEVATED_VOL | Yes | 0.5 | VIX 20 to 28. Trade smaller, tighter buffers |
| BREAKOUT | Yes | 0.5 | SPX broke out or down. Directional bias, cautious |
| PANIC | No | 0.0 | VIX above 32 or 20%+ 1-day spike. NO-TRADE |
| LOW_VOL_NO_EDGE | No | 0.0 | VIX below 12. Premium too cheap. NO-TRADE |

Decision tree, in priority order:
1. VIX 1-day spike at or above the threshold (default 20%) -> PANIC.
2. VIX above panic floor (default 32) -> PANIC.
3. VIX at or below floor (default 12) -> LOW_VOL_NO_EDGE.
4. SPX breakout or breakdown beyond N-day high/low (default 0.5% buffer) -> BREAKOUT.
5. Bollinger band width compressed to at most 50% of average -> COMPRESSION.
6. VIX above benign max (default 20) -> ELEVATED_VOL.
7. SPX above slow SMA (default 50d) -> BENIGN_TREND, else BENIGN_CHOP.

All thresholds live in `options_system/config/regime_config.yaml` and can be
tuned without code changes.

## Scanner

The scanner takes a configurable universe and screens each ticker against
several filters. A candidate must pass every filter to advance.

Default universe:
- Index ETFs: SPY, QQQ, IWM
- Defensive equities: PG, KO, JNJ, PEP, ABBV, XLP, XLU, XLV, MCD, CL, WMT

Filters:
- **Dollar volume** in underlying at least $5M average over 20 days.
- **Available expirations** in the 14-21 DTE window. Otherwise rejected.
- **Near-ATM IV** (median of contracts within 5% of spot) must fall between
  15% and 80% (configurable).
- **IV-rank proxy** (realized-vol percentile over 252d) at or above 30th
  percentile.
- **Chain liquidity** at the ATM region: at least 25% of contracts within
  10% of spot must have OI >= 100 and bid-ask spread <= 10% of mid.
- **Realized-vol compression** (either ATR ratio <= 75% of trailing average,
  or BB-width ratio <= 65% of trailing average). The "compression" filter is
  enabled by default and can be turned off in config.

Candidates are scored on IV centering, compression depth, dollar volume, and
IV-rank, then ranked.

All thresholds live in `options_system/config/scanner_config.yaml`.

## Trade Builder

For each surviving candidate, the builder constructs trade proposals at
every expiration in the DTE window. It tries every width in the configured
set (1.0, 1.75, 2.5, 3.75, 5.0 by default), on both the put side and the
call side, plus iron condors that combine both sides.

### Strike Selection

The builder targets a short-strike distance from spot that depends on
whether the ticker is an "index product" or an "equity":

- **Index products** (SPY, QQQ, IWM, SPX, NDX, RUT): VIX-tiered expected
  move multiplier:
  - VIX <= 14: 1.25x expected move
  - VIX 14 to 18: 1.5x expected move
  - VIX 18 to 24: 2.0x expected move
  - VIX > 24: 2.5x expected move
- **Equities** (PG, KO, JNJ, etc.): 1.5x ATR (14-day, configurable).

The VIX tiering is the Phase 1.5 fix to a Phase 1 problem where a flat 2x
expected-move rule locked the system out of SPX trades in benign VIX. The
new rule trades SPX selectively in low vol instead of refusing.

### Credit and POP

- **Credit** = short leg mid minus long leg mid.
- **POP (probability of profit)** is approximated as `1 - |short delta|`,
  which is the standard back-of-envelope for an OTM short.
- **Credit-to-width ratio** must fall between 8% and 45% (configurable).
  Below 8%, the spread is too thin to justify the risk. Above 45%, the
  spread is priced for a known event and likely a trap.
- **POP target band** is 70% to 90%, with 80% as the ranking center.

### Risk Metrics

This is where Phase 1.5 introduced the most important change. The system now
computes two separate flip points:

**Early-red M2M flip** (path-aware, the one the client cares about for live
risk):

The underlying price at which, 5 days forward from entry, the spread's
mark-to-market loss equals 25% of credit collected. Both the 5-day window
and the 25% loss threshold are configurable in
`options_system/config/strategy_rules.yaml` under the `m2m` block.

This is what the client means by "first meaningful M2M loss." It accounts
for theta decay over the first few days, which is what creates the buffer
that lets the trade survive small adverse moves. The further this flip is
from spot, the more cushion the trade has before going meaningfully red.

**Expiration breakeven** (textbook trader definition, secondary reference):

Short strike plus or minus credit. The price at which the trade is exactly
flat at expiration. This is shown alongside as context but it is NOT the
primary risk number. For a typical credit spread the expiration breakeven
is further from spot than the early-red flip. On a live PG bull-put example
the early-red flip was 3.0% from spot while the expiration breakeven was
4.6%. The difference is the gap between "where the trade goes red on M2M
this week" and "where I lose money if I hold to the end."

### Resilience Score

A 0-to-1 score, higher is more resilient. The builder runs the spread
through approximately 60 stress scenarios per trade: 4 adverse spot levels
(0.25, 0.5, 0.75, and 1.0 ATR multiples) times 3 IV-shock levels (flat,
+5 vol points, +10 vol points) times 5 forward days. Each scenario re-prices
the spread under stress. The score is the fraction of scenarios in which
the spread mark stays at or below entry credit (i.e. the trade is not red).

Phase 1.5 added the IV-shock dimension. Phase 1's version only tested
adverse spot moves at flat IV, which missed the volatility-expansion risk
that triggers most early red trades. The new version is closer to a real
stress test, but it still assumes independent, single-day shocks. It does
not model momentum continuation, autocorrelated path dependence, or skew
shifts. Those are Phase 2 candidates.

### Ranking

Each proposal gets a rank score based on:
- POP centering (closeness to the 80% target)
- M2M flip distance from spot (more is better, scaled vs expected move)
- Credit-to-width sweet spot (peaks around 30%)
- Liquidity (tight bid-ask)
- Resilience score (early-red P/L durability)

Penalties are applied for:
- Early-red M2M flip within 1.0% of spot (auto-reject) or 2.0% (warn).
- Expiration breakeven within 1.5% (auto-reject) or 3.0% (warn).
- Resilience score below 0.4 (early-red vulnerable flag).

All weights and thresholds live in YAML.

## Validator

Just before manual entry, the validator refetches the option chain and
re-checks the trade. This catches situations where the market moved
between when the system found the trade and when the human is about to
click. Specific checks:

- **Regime gate still open.** If the regime flipped to NO-TRADE in the
  interim, the trade is invalid.
- **Credit drift.** Recomputes credit from the fresh quotes. If the change
  exceeds 15% in either direction, the trade is invalid (the market moved
  enough that the original analysis is stale).
- **Liquidity still acceptable.** Flags wide bid-ask spreads but does not
  reject for them alone.
- **IV ceiling.** If any leg's IV blew out above the configured 80% cap,
  the trade is invalid (suggests an event we missed).
- **Early-red M2M flip distance.** If the flip is within 1.0% of fresh
  spot, the trade is invalid.
- **Gamma window.** If DTE is at or below the no-open threshold (default 5
  days), the trade is invalid.

The output is `VALID` (OK to enter) or `INVALID` (do not enter) with a
list of reasons. Non-blocking warnings (wide spread, fresh IV slightly
elevated) are shown separately.

## Failure Logic

After a trade is on, the system can be asked to evaluate the open
position. It will return exit signals at three severities:
- `EXIT`: close the position now.
- `WARN`: position is approaching trouble.
- `INFO`: a profit target was hit (consider scaling).

Default exit signals:
- **Profit target hit at 50%** of credit (exit half or all).
- **Profit target hit at 25%** of credit (info, consider scaling).
- **Loss exceeds 2x credit** (configurable multiplier).
- **Loss exceeds 60% of width.**
- **Loss exceeds the hard dollar stop** (default $200 per spread, the
  client's `-$200 rule`). This is independent of credit/width math and
  applies as an absolute floor.
- **Underlying within 3% of early-red M2M flip** (warn).
- **DTE at or below 7** (gamma hot zone, scale toward exit).
- **DTE at or below 2** (force close regardless of P/L).
- **Structure-break trigger** (close above prior swing high or below
  prior swing low).

All thresholds live in `options_system/config/failure_logic.yaml`.

## Execution Output

For each VALID trade, the system produces a trade card with:
- **Legs**: per-leg side, right (call/put), strike, expiry, bid/ask/mid,
  delta, and the OCC contract symbol.
- **Order**: limit price suggestion (mid plus 30% of the way to natural),
  credit target, width, max loss, POP, credit/width ratio.
- **Risk panel**: early-red M2M flip with direction (above/below spot),
  expiration breakeven, expected move, ATR, resilience score, flags.
- **Management**: 50% and 25% exit targets, hard stop, time stop.

The card is mobile-readable and maps one-to-one to Robinhood's custom
option order ticket.

## Limitations and Approximations

These are real and need to be understood before trusting the numbers.

- **Greeks are computed via Black-Scholes**, not received from yfinance.
  yfinance does not return greeks consistently. The IV is taken from the
  chain when present and solved via Brent when missing.
- **POP is approximated as 1 minus delta**, which is a first-order
  estimate. Actual POP depends on the full distribution at expiration.
- **Resilience score uses independent shocks**, not correlated paths. A
  Monte Carlo over correlated price/vol paths would be more accurate.
- **No momentum-based exits** yet. The system does not detect "the trend
  is accelerating against the trade." That requires Phase 2 work and the
  client's specific definition.
- **Backtest chains are synthetic.** The backtester reconstructs option
  chains using Black-Scholes priced off realized vol with a small term
  structure tilt. No skew. Backtest absolute returns should be treated as
  directionally indicative, not exact.
- **yfinance is rate-limited and occasionally flaky.** The data adapter
  caches aggressively and retries with backoff, but some scan runs drop
  tickers that would otherwise pass. This is most visible in dense morning
  scans.
- **Execution is manual.** No broker integration. Slippage and partial
  fills are the human's problem to manage on Robinhood.

## Phase 1.5 Changes (May 2026)

These shipped after the Phase 1 review:

1. **M2M flip redefined as path-aware early-red price** (5d / 25% credit
   loss). The Phase 1 version used the expiration breakeven, which was
   not what the client meant. Both definitions are now shown.
2. **Resilience score now includes IV-shock scenarios.** Phase 1 only
   tested adverse spot moves at flat IV. The new version is roughly 3x
   the scenario count and captures vol expansion risk.
3. **SPX buffer tiered by VIX.** Phase 1 used a flat 2x expected-move rule
   which locked the system out of SPX in benign VIX. New schedule is
   1.25x calm, 1.5x benign, 2x normal, 2.5x elevated.
4. **Hard dollar-loss stop wired in.** The client's `-$200 per spread`
   rule is now a configurable failure signal. Independent of credit/width
   geometry.

## Phase 2 Open Items

Items still on the roadmap, in rough priority order:

1. **Path-aware momentum exits.** Detect "the trade is going against me
   on accelerating momentum" before the dollar stop is hit. Requires the
   client's specific definition of "approaching the danger zone."
2. **Calibration against real trades.** The single most valuable Phase 2
   input is the client's notes on (a) trades the system marked VALID that
   the client would skip, (b) trades the client would take that the
   system did not surface, (c) trades that went red faster than the
   early-red flip suggested. That dataset tunes the model to the client.
3. **Broker API integration.** Tradier or Schwab. Removes manual entry.
4. **Real historical option chains** for backtests. Polygon or CBOE
   Datashop. Replaces the synthetic-chain approximation.
5. **Position management dashboard.** Track live open positions, show
   running P/L, surface exit signals as they trigger. Today the system
   can evaluate a position you describe to it, but does not watch your
   portfolio on its own.
6. **More accurate POP.** Current POP is `1 minus absolute delta of
   short leg`, a first-order estimate. A full distribution-based POP
   (or vol-surface-adjusted) would be marginally better.
7. **Correlated-path resilience score.** Today's score uses independent
   single-day shocks across spot and IV. A Monte Carlo over correlated
   paths would model momentum continuation and joint distributions.
8. **Optional HMM-based regime layer** alongside the rules engine. A
   second opinion on the deploy/no-trade gate.
9. **CI/CD.** Tests run locally today (13 unit tests across regime,
   greeks, failure logic). No GitHub Actions workflow yet. Phase 2 add.
10. **Alerting.** No SMS/email/Slack alerts today. When a trade
    surfaces, the user has to be looking at the dashboard. A simple
    daily-digest email or push notification is a small Phase 2 addition.

## Connecting an AI Advisor to the Scanner

Grant asked about connecting Chat directly to the scanner. Here is how
that would work and what the trade-offs are.

**What is possible:**
- Build a small HTTP API on top of the scanner output. The advisor (Chat
  or Claude or a custom GPT) calls the API to get today's regime, today's
  candidates, and the trade detail for a specific candidate. The advisor
  reads the structured response and reasons over it.
- Build a periodic "digest" file that the system writes daily (markdown or
  JSON). The advisor reads the digest at the start of each session.
- Build a dedicated Claude or GPT instance configured as a custom assistant
  that has the scanner data preloaded into its context, refreshed daily.

**What changes versus the current Chat session:**
- **Memory does not carry over.** A new AI integration is a new session.
  Whatever conversational history Grant has built up with Chat does not
  transfer. The advisor starts fresh each time, with only the system data
  and whatever system prompt is configured.
- **Per-use cost.** The current Chat session is on whatever subscription
  Grant pays for. A dedicated integration is billed per API call, roughly
  in the cents-to-low-dollars per session range depending on volume.
- **Latency.** The current Chat session is interactive. An integrated
  advisor that fetches scanner data adds 1-3 seconds per query.

**Recommended sequencing:**
- **Short-term (now):** Grant or Chat reads this README plus the live
  dashboard. That gives Chat full system context without any new
  integration work.
- **Medium-term (Phase 2):** stand up the digest file. Each daily run
  writes a structured summary that Chat can ingest by paste or by upload.
- **Longer-term (Phase 3):** build the API and a custom GPT or Claude
  assistant. This requires deciding which AI vendor to use, setting up
  billing, and committing to a maintenance cadence.

## Configuration Files

All thresholds are decoupled from code. Files live under
`options_system/config/`:

- `strategy_rules.yaml`: POP band, DTE window, buffer schedules, exit
  ladder, M2M definition, ranking weights.
- `regime_config.yaml`: VIX bands, SPX trend/breakout/compression rules,
  regime-to-deploy map.
- `failure_logic.yaml`: Loss tolerance (multiple of credit, percent of
  width, hard dollar stop), M2M proximity thresholds, gamma zones,
  structure-break rules.
- `scanner_config.yaml`: Universe of tickers, IV filters, liquidity
  thresholds, compression settings.
- `data_config.yaml`: Provider choice (yfinance for Phase 1), cache TTLs,
  retry behavior, risk-free rate proxy for Black-Scholes.

Editing a YAML file is enough to change behavior. No code changes required.

## Dashboard

The Streamlit dashboard has 6 pages:

1. **Overview**: pipeline status, regime banner, quick counts.
2. **Regime Overview**: VIX and SPX charts with band overlays, classifier
   reasoning, deployment map.
3. **Today's Candidates**: ranked color-coded table with strikes, credit,
   POP, early-red flip, expiration breakeven, exit levels.
4. **Trade Detail**: full execution card for any proposal, validation
   status, failure-logic flags, exit ladder, copy-paste text card.
5. **Log Viewer**: searchable history of past scans, decisions, and trades.
6. **Daily Snapshot**: single plain-text dump of today's regime,
   candidates, and top proposals, formatted for paste-in to an outside
   AI advisor (Chat, ChatGPT, Claude). Streamlit pages render via
   JavaScript so external AIs cannot reliably browse the dashboard URL
   directly; this page exists as a copy-pasteable bridge.

The sidebar includes a **Replay mode** that lets the user point the
pipeline at any past date in the last two years. Real OHLCV and VIX
history, synthetic chains. Useful for showing populated pages when
today's live regime returns no candidates.

A purple "Replay mode" banner sits at the top of every page when this is
on, so live and replay are never confused.

If Yahoo Finance is having an outage (occasionally yfinance returns
malformed responses), the pages show a clear error banner rather than
crashing, and Replay mode keeps working since it uses cached history.

## Glossary

- **Bull put**: short an OTM put, long a further OTM put. Bullish, profit
  if underlying stays above the short strike at expiration.
- **Bear call**: short an OTM call, long a further OTM call. Bearish,
  profit if underlying stays below the short strike at expiration.
- **Iron condor**: bull put plus bear call, same expiry. Neutral, profit
  if underlying stays inside both short strikes.
- **DTE**: days to expiration.
- **POP**: probability of profit. The chance the trade ends profitable.
- **Credit**: net premium received when the trade is opened.
- **Width**: difference between short and long strikes. Defines max loss.
- **M2M**: mark-to-market. Current value of the position if closed now.
- **Early-red flip**: the underlying price level at which the trade's
  mark-to-market goes meaningfully red within the first few days.
  See risk definitions above for the precise calculation.
- **Expiration breakeven**: the underlying price at which the trade is
  exactly flat at expiration. Short strike plus or minus credit.
- **Resilience score**: 0 to 1, the fraction of stress scenarios in which
  the spread mark stays at or below entry credit (i.e. not red).
- **VIX**: implied volatility index for SPX. Proxy for market vol.
- **ATR**: average true range. Daily price-range proxy.
- **Expected move**: 1 standard deviation move to expiration, computed as
  spot times IV times square-root of time.
