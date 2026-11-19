# Grant Options Income System — Daily Snapshot

Generated: 2026-11-19 21:10 UTC (live data)
Generated (Pacific): Thursday, November 19, 2026 at 01:10 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BREAKOUT
Decision: DEPLOY
Size multiplier: 0.50
  - SPX breakout down

## Candidates
- INTC: score 0.32, spot $55.72, near-ATM IV 78.3%, ATR $4.39

## Trade Proposals
### #1: INTC BULL_PUT exp 2026-12-04 (15 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 95, M2M Distance 15, Credit Quality 55, Liquidity 0, Resilience 7)
  Leg: SELL Put $49.00 mid 1.15
  Leg: BUY Put $46.00 mid 0.65
  Spot $55.72  Credit $0.50  Width $3.00  POP 81%
  Early-red M2M flip: $52.80 (5.24% below spot)
  Expiration breakeven: $48.51  Resilience: 0.07
  Exits: 50% at $0.25, 25% at $0.37
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

### #2: INTC BULL_PUT exp 2026-12-04 (15 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 95, M2M Distance 16, Credit Quality 50, Liquidity 0, Resilience 8)
  Leg: SELL Put $49.00 mid 1.15
  Leg: BUY Put $44.00 mid 0.40
  Spot $55.72  Credit $0.74  Width $5.00  POP 81%
  Early-red M2M flip: $52.57 (5.66% below spot)
  Expiration breakeven: $48.26  Resilience: 0.08
  Exits: 50% at $0.37, 25% at $0.56
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.