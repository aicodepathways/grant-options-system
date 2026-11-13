# Grant Options Income System — Daily Snapshot

Generated: 2026-11-13 20:18 UTC (live data)
Generated (Pacific): Friday, November 13, 2026 at 12:18 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- BAC: score 0.53, spot $50.78, near-ATM IV 23.8%, ATR $1.16

## Trade Proposals
### #1: BAC BULL_PUT exp 2026-11-27 (14 DTE)
  Mode: INCOME
  Overall score: 19/100 (POP Fit 95, M2M Distance 15, Credit Quality 52, Liquidity 0, Resilience 5)
  Leg: SELL Put $49.00 mid 0.33
  Leg: BUY Put $48.00 mid 0.17
  Spot $50.78  Credit $0.16  Width $1.00  POP 79%
  Early-red M2M flip: $49.99 (1.55% below spot)
  Expiration breakeven: $48.84  Resilience: 0.05
  Exits: 50% at $0.08, 25% at $0.12
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: BAC BULL_PUT exp 2026-12-04 (21 DTE)
  Mode: INCOME
  Overall score: 18/100 (POP Fit 67, M2M Distance 13, Credit Quality 77, Liquidity 0, Resilience 3)
  Leg: SELL Put $49.00 mid 0.58
  Leg: BUY Put $48.00 mid 0.35
  Spot $50.78  Credit $0.23  Width $1.00  POP 73%
  Early-red M2M flip: $49.92 (1.69% below spot)
  Expiration breakeven: $48.77  Resilience: 0.03
  Exits: 50% at $0.12, 25% at $0.17
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.