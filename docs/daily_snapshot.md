# Grant Options Income System — Daily Snapshot

Generated: 2026-11-04 20:15 UTC (live data)
Generated (Pacific): Wednesday, November 04, 2026 at 12:15 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- GS: score 0.49, spot $927.47, near-ATM IV 32.5%, ATR $24.91

## Trade Proposals
### #1: GS BULL_PUT exp 2026-11-20 (16 DTE)
  Mode: INCOME
  Overall score: 29/100 (POP Fit 77, M2M Distance 11, Credit Quality 72, Liquidity 78, Resilience 2)
  Leg: SELL Put $887.50 mid 10.62
  Leg: BUY Put $882.50 mid 9.55
  Spot $926.23  Credit $1.07  Width $5.00  POP 75%
  Early-red M2M flip: $910.07 (1.74% below spot)
  Expiration breakeven: $886.42  Resilience: 0.02
  Exits: 50% at $0.54, 25% at $0.81
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: GS BULL_PUT exp 2026-11-20 (16 DTE)
  Mode: INCOME
  Overall score: 29/100 (POP Fit 77, M2M Distance 11, Credit Quality 72, Liquidity 78, Resilience 2)
  Leg: SELL Put $887.50 mid 10.62
  Leg: BUY Put $882.50 mid 9.55
  Spot $926.23  Credit $1.07  Width $5.00  POP 75%
  Early-red M2M flip: $910.07 (1.74% below spot)
  Expiration breakeven: $886.42  Resilience: 0.02
  Exits: 50% at $0.54, 25% at $0.81
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.