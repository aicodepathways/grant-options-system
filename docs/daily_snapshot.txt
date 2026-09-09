# Grant Options Income System — Daily Snapshot

Generated: 2026-09-09 04:16 UTC (live data)
Generated (Pacific): Tuesday, September 08, 2026 at 09:16 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: COMPRESSION
Decision: DEPLOY
Size multiplier: 1.00
  - SPX BB-width compressed: 0.0238 <= 50% of avg 0.0486

## Candidates
- TSLA: score 0.65, spot $368.16, near-ATM IV 42.1%, ATR $15.80

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-09-25 (17 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 87, M2M Distance 12, Credit Quality 52, Liquidity 73, Resilience 2)
  Leg: SELL Put $340.00 mid 3.35
  Leg: BUY Put $335.00 mid 2.57
  Spot $368.16  Credit $0.78  Width $5.00  POP 83%
  Early-red M2M flip: $359.00 (2.49% below spot)
  Expiration breakeven: $339.22  Resilience: 0.02
  Exits: 50% at $0.39, 25% at $0.58
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-09-25 (17 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 87, M2M Distance 12, Credit Quality 52, Liquidity 73, Resilience 2)
  Leg: SELL Put $340.00 mid 3.35
  Leg: BUY Put $335.00 mid 2.57
  Spot $368.16  Credit $0.78  Width $5.00  POP 83%
  Early-red M2M flip: $359.00 (2.49% below spot)
  Expiration breakeven: $339.22  Resilience: 0.02
  Exits: 50% at $0.39, 25% at $0.58
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.