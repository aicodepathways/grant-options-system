# Grant Options Income System — Daily Snapshot

Generated: 2026-11-26 22:06 UTC (live data)
Generated (Pacific): Thursday, November 26, 2026 at 02:06 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: ELEVATED_VOL
Decision: DEPLOY
Size multiplier: 0.50
  - VIX 26.80 elevated (>20.0)

## Candidates
- META: score 0.66, spot $609.89, near-ATM IV 50.5%, ATR $24.32

## Trade Proposals
### #1: META BEAR_CALL exp 2026-12-11 (15 DTE)
  Mode: INCOME
  Overall score: 28/100 (POP Fit 62, M2M Distance 13, Credit Quality 92, Liquidity 22, Resilience 5)
  Leg: SELL Call $650.00 mid 9.48
  Leg: BUY Call $655.00 mid 8.10
  Spot $609.89  Credit $1.38  Width $5.00  POP 72%
  Early-red M2M flip: $628.74 (3.09% above spot)
  Expiration breakeven: $651.38  Resilience: 0.05
  Exits: 50% at $0.69, 25% at $1.03
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

### #2: META BEAR_CALL exp 2026-12-11 (15 DTE)
  Mode: INCOME
  Overall score: 28/100 (POP Fit 62, M2M Distance 13, Credit Quality 92, Liquidity 22, Resilience 5)
  Leg: SELL Call $650.00 mid 9.48
  Leg: BUY Call $655.00 mid 8.10
  Spot $609.89  Credit $1.38  Width $5.00  POP 72%
  Early-red M2M flip: $628.74 (3.09% above spot)
  Expiration breakeven: $651.38  Resilience: 0.05
  Exits: 50% at $0.69, 25% at $1.03
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.