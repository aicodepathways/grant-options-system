# Grant Options Income System — Daily Snapshot

Generated: 2026-07-24 14:13 UTC (live data)

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- WMT: score 0.45, spot $108.83, near-ATM IV 25.0%, ATR $2.39

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-08-07 (14 DTE)
  Mode: INCOME
  Overall score: 24/100 (POP Fit 96, M2M Distance 19, Credit Quality 50, Liquidity 0, Resilience 25)
  Leg: SELL Put $105.00 mid 0.72
  Leg: BUY Put $104.00 mid 0.57
  Spot $108.83  Credit $0.15  Width $1.00  POP 79%
  Early-red M2M flip: $106.55 (2.09% below spot)
  Expiration breakeven: $104.85  Resilience: 0.25
  Exits: 50% at $0.07, 25% at $0.11
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: WMT BULL_PUT exp 2026-08-07 (14 DTE)
  Mode: INCOME
  Overall score: 22/100 (POP Fit 96, M2M Distance 17, Credit Quality 48, Liquidity 0, Resilience 17)
  Leg: SELL Put $105.00 mid 0.72
  Leg: BUY Put $103.00 mid 0.43
  Spot $108.83  Credit $0.29  Width $2.00  POP 79%
  Early-red M2M flip: $106.77 (1.89% below spot)
  Expiration breakeven: $104.71  Resilience: 0.17
  Exits: 50% at $0.14, 25% at $0.22
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.