# Grant Options Income System — Daily Snapshot

Generated: 2026-11-13 23:17 UTC (live data)
Generated (Pacific): Friday, November 13, 2026 at 03:17 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- BAC: score 0.54, spot $51.02, near-ATM IV 24.0%, ATR $1.17

## Trade Proposals
### #1: BAC BEAR_CALL exp 2026-11-27 (14 DTE)
  Mode: INCOME
  Overall score: 19/100 (POP Fit 100, M2M Distance 15, Credit Quality 47, Liquidity 0, Resilience 5)
  Leg: SELL Call $53.00 mid 0.23
  Leg: BUY Call $54.00 mid 0.09
  Spot $51.02  Credit $0.14  Width $1.00  POP 80%
  Early-red M2M flip: $51.83 (1.58% above spot)
  Expiration breakeven: $53.14  Resilience: 0.05
  Exits: 50% at $0.07, 25% at $0.10
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: BAC BULL_PUT exp 2026-12-04 (21 DTE)
  Mode: INCOME
  Overall score: 19/100 (POP Fit 75, M2M Distance 13, Credit Quality 73, Liquidity 0, Resilience 3)
  Leg: SELL Put $49.00 mid 0.54
  Leg: BUY Put $48.00 mid 0.32
  Spot $51.02  Credit $0.22  Width $1.00  POP 75%
  Early-red M2M flip: $50.13 (1.75% below spot)
  Expiration breakeven: $48.78  Resilience: 0.03
  Exits: 50% at $0.11, 25% at $0.17
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.