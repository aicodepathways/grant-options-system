# Grant Options Income System — Daily Snapshot

Generated: 2026-08-21 14:16 UTC (live data)
Generated (Pacific): Friday, August 21, 2026 at 07:16 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- QQQ: score 0.32, spot $710.09, near-ATM IV 19.4%, ATR $9.69

## Trade Proposals
### #1: QQQ BEAR_CALL exp 2026-09-04 (14 DTE)
  Mode: OPPORTUNITY
  Overall score: 26/100 (POP Fit 88, M2M Distance 13, Credit Quality 92, Liquidity 86, Resilience 3)
  Leg: SELL Call $724.00 mid 5.54
  Leg: BUY Call $729.00 mid 3.92
  Spot $710.09  Credit $1.62  Width $5.00  POP 67%
  Early-red M2M flip: $718.20 (1.14% above spot)
  Expiration breakeven: $725.62  Resilience: 0.03
  Exits: 50% at $0.81, 25% at $1.21
  Validation: VALID
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #2: QQQ BEAR_CALL exp 2026-09-04 (14 DTE)
  Mode: OPPORTUNITY
  Overall score: 26/100 (POP Fit 88, M2M Distance 13, Credit Quality 92, Liquidity 85, Resilience 3)
  Leg: SELL Call $724.00 mid 5.54
  Leg: BUY Call $728.00 mid 4.23
  Spot $710.09  Credit $1.30  Width $4.00  POP 67%
  Early-red M2M flip: $718.11 (1.13% above spot)
  Expiration breakeven: $725.30  Resilience: 0.03
  Exits: 50% at $0.65, 25% at $0.98
  Validation: VALID
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.