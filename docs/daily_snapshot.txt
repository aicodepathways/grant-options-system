# Grant Options Income System — Daily Snapshot

Generated: 2026-10-21 17:53 UTC (live data)
Generated (Pacific): Wednesday, October 21, 2026 at 10:53 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- META: score 0.63, spot $708.15, near-ATM IV 51.9%, ATR $22.36
- NFLX: score 0.48, spot $65.77, near-ATM IV 30.9%, ATR $1.92

## Trade Proposals
### #1: META BULL_PUT exp 2026-11-06 (16 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 61, M2M Distance 11, Credit Quality 88, Liquidity 56, Resilience 5)
  Leg: SELL Put $670.00 mid 14.93
  Leg: BUY Put $665.00 mid 13.60
  Spot $708.20  Credit $1.32  Width $5.00  POP 72%
  Early-red M2M flip: $688.45 (2.79% below spot)
  Expiration breakeven: $668.67  Resilience: 0.05
  Exits: 50% at $0.66, 25% at $0.99
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: META BULL_PUT exp 2026-11-06 (16 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 61, M2M Distance 11, Credit Quality 88, Liquidity 56, Resilience 5)
  Leg: SELL Put $670.00 mid 14.93
  Leg: BUY Put $665.00 mid 13.60
  Spot $708.20  Credit $1.32  Width $5.00  POP 72%
  Early-red M2M flip: $688.45 (2.79% below spot)
  Expiration breakeven: $668.67  Resilience: 0.05
  Exits: 50% at $0.66, 25% at $0.99
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: NFLX BEAR_CALL exp 2026-11-06 (16 DTE)
  Mode: INCOME
  Overall score: 17/100 (POP Fit 76, M2M Distance 12, Credit Quality 58, Liquidity 16, Resilience 2)
  Leg: SELL Call $69.00 mid 0.62
  Leg: BUY Call $70.00 mid 0.45
  Spot $65.62  Credit $0.18  Width $1.00  POP 75%
  Early-red M2M flip: $66.73 (1.69% above spot)
  Expiration breakeven: $69.17  Resilience: 0.02
  Exits: 50% at $0.09, 25% at $0.13
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: NFLX BULL_PUT exp 2026-11-06 (16 DTE)
  Mode: INCOME
  Overall score: 17/100 (POP Fit 84, M2M Distance 14, Credit Quality 52, Liquidity 0, Resilience 5)
  Leg: SELL Put $62.00 mid 0.42
  Leg: BUY Put $61.00 mid 0.26
  Spot $65.62  Credit $0.16  Width $1.00  POP 83%
  Early-red M2M flip: $64.26 (2.07% below spot)
  Expiration breakeven: $61.84  Resilience: 0.05
  Exits: 50% at $0.08, 25% at $0.12
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.