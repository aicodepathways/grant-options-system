# Grant Options Income System — Daily Snapshot

Generated: 2026-10-19 22:02 UTC (live data)
Generated (Pacific): Monday, October 19, 2026 at 03:02 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- META: score 0.67, spot $705.44, near-ATM IV 49.7%, ATR $21.41

## Trade Proposals
### #1: META BULL_PUT exp 2026-11-06 (18 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 54, M2M Distance 12, Credit Quality 97, Liquidity 61, Resilience 5)
  Leg: SELL Put $670.00 mid 16.05
  Leg: BUY Put $665.00 mid 14.50
  Spot $705.44  Credit $1.55  Width $5.00  POP 71%
  Early-red M2M flip: $684.08 (3.03% below spot)
  Expiration breakeven: $668.45  Resilience: 0.05
  Exits: 50% at $0.78, 25% at $1.16
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

### #2: META BULL_PUT exp 2026-11-06 (18 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 54, M2M Distance 12, Credit Quality 97, Liquidity 61, Resilience 5)
  Leg: SELL Put $670.00 mid 16.05
  Leg: BUY Put $665.00 mid 14.50
  Spot $705.44  Credit $1.55  Width $5.00  POP 71%
  Early-red M2M flip: $684.08 (3.03% below spot)
  Expiration breakeven: $668.45  Resilience: 0.05
  Exits: 50% at $0.78, 25% at $1.16
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.