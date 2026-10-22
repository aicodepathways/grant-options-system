# Grant Options Income System — Daily Snapshot

Generated: 2026-10-22 21:14 UTC (live data)
Generated (Pacific): Thursday, October 22, 2026 at 02:14 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- META: score 0.56, spot $648.85, near-ATM IV 39.9%, ATR $25.57

## Trade Proposals
### #1: META BULL_PUT exp 2026-11-06 (15 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 98, M2M Distance 13, Credit Quality 67, Liquidity 28, Resilience 3)
  Leg: SELL Put $610.00 mid 6.70
  Leg: BUY Put $605.00 mid 5.70
  Spot $648.85  Credit $1.00  Width $5.00  POP 80%
  Early-red M2M flip: $633.77 (2.32% below spot)
  Expiration breakeven: $609.00  Resilience: 0.03
  Exits: 50% at $0.50, 25% at $0.75
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: META BULL_PUT exp 2026-11-06 (15 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 98, M2M Distance 13, Credit Quality 67, Liquidity 28, Resilience 3)
  Leg: SELL Put $610.00 mid 6.70
  Leg: BUY Put $605.00 mid 5.70
  Spot $648.85  Credit $1.00  Width $5.00  POP 80%
  Early-red M2M flip: $633.77 (2.32% below spot)
  Expiration breakeven: $609.00  Resilience: 0.03
  Exits: 50% at $0.50, 25% at $0.75
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.