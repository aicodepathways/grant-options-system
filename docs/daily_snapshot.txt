# Grant Options Income System — Daily Snapshot

Generated: 2026-11-04 23:15 UTC (live data)
Generated (Pacific): Wednesday, November 04, 2026 at 03:15 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- GS: score 0.49, spot $928.00, near-ATM IV 32.9%, ATR $24.91

## Trade Proposals
### #1: GS BULL_PUT exp 2026-11-20 (16 DTE)
  Mode: INCOME
  Overall score: 33/100 (POP Fit 74, M2M Distance 13, Credit Quality 83, Liquidity 79, Resilience 7)
  Leg: SELL Put $890.00 mid 10.95
  Leg: BUY Put $887.50 mid 10.32
  Spot $928.00  Credit $0.62  Width $2.50  POP 75%
  Early-red M2M flip: $908.62 (2.09% below spot)
  Expiration breakeven: $889.38  Resilience: 0.07
  Exits: 50% at $0.31, 25% at $0.47
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: GS BULL_PUT exp 2026-11-20 (16 DTE)
  Mode: INCOME
  Overall score: 33/100 (POP Fit 74, M2M Distance 13, Credit Quality 83, Liquidity 79, Resilience 7)
  Leg: SELL Put $890.00 mid 10.95
  Leg: BUY Put $887.50 mid 10.32
  Spot $928.00  Credit $0.62  Width $2.50  POP 75%
  Early-red M2M flip: $908.62 (2.09% below spot)
  Expiration breakeven: $889.38  Resilience: 0.07
  Exits: 50% at $0.31, 25% at $0.47
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.