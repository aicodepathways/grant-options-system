# Grant Options Income System — Daily Snapshot

Generated: 2026-07-29 15:33 UTC (live data)

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- WMT: score 0.51, spot $113.22, near-ATM IV 26.5%, ATR $2.44

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-08-14 (16 DTE)
  Mode: INCOME
  Overall score: 19/100 (POP Fit 87, M2M Distance 13, Credit Quality 63, Liquidity 0, Resilience 5)
  Leg: SELL Put $109.00 mid 0.90
  Leg: BUY Put $107.00 mid 0.52
  Spot $113.22  Credit $0.38  Width $2.00  POP 77%
  Early-red M2M flip: $111.41 (1.61% below spot)
  Expiration breakeven: $108.62  Resilience: 0.05
  Exits: 50% at $0.19, 25% at $0.28
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: WMT BEAR_CALL exp 2026-08-14 (16 DTE)
  Mode: INCOME
  Overall score: 18/100 (POP Fit 51, M2M Distance 12, Credit Quality 83, Liquidity 16, Resilience 3)
  Leg: SELL Call $117.00 mid 1.10
  Leg: BUY Call $118.00 mid 0.85
  Spot $113.22  Credit $0.25  Width $1.00  POP 70%
  Early-red M2M flip: $114.98 (1.55% above spot)
  Expiration breakeven: $117.25  Resilience: 0.03
  Exits: 50% at $0.12, 25% at $0.19
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.