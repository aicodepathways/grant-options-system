# Grant Options Income System — Daily Snapshot

Generated: 2026-10-23 21:03 UTC (live data)
Generated (Pacific): Friday, October 23, 2026 at 02:03 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- GLD: score 0.44, spot $366.61, near-ATM IV 22.5%, ATR $5.33

## Trade Proposals
### #1: GLD BULL_PUT exp 2026-11-06 (14 DTE)
  Mode: INCOME
  Overall score: 13/100 (POP Fit 87, M2M Distance 14, Credit Quality 57, Liquidity 32, Resilience 8)
  Leg: SELL Put $355.00 mid 2.52
  Leg: BUY Put $350.00 mid 1.67
  Spot $366.61  Credit $0.85  Width $5.00  POP 77%
  Early-red M2M flip: $361.54 (1.38% below spot)
  Expiration breakeven: $354.15  Resilience: 0.08
  Exits: 50% at $0.43, 25% at $0.64
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #2: GLD BULL_PUT exp 2026-11-06 (14 DTE)
  Mode: INCOME
  Overall score: 13/100 (POP Fit 87, M2M Distance 14, Credit Quality 57, Liquidity 32, Resilience 8)
  Leg: SELL Put $355.00 mid 2.52
  Leg: BUY Put $350.00 mid 1.67
  Spot $366.61  Credit $0.85  Width $5.00  POP 77%
  Early-red M2M flip: $361.54 (1.38% below spot)
  Expiration breakeven: $354.15  Resilience: 0.08
  Exits: 50% at $0.43, 25% at $0.64
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.