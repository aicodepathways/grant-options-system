# Grant Options Income System — Daily Snapshot

Generated: 2026-11-12 20:38 UTC (live data)
Generated (Pacific): Thursday, November 12, 2026 at 12:38 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- BAC: score 0.52, spot $50.56, near-ATM IV 23.5%, ATR $1.20

## Trade Proposals
### #1: BAC BEAR_CALL exp 2026-11-27 (15 DTE)
  Mode: INCOME
  Overall score: 12/100 (POP Fit 86, M2M Distance 14, Credit Quality 27, Liquidity 0, Resilience 3)
  Leg: SELL Call $53.00 mid 0.21
  Leg: BUY Call $55.00 mid 0.04
  Spot $50.56  Credit $0.16  Width $2.00  POP 83%
  Early-red M2M flip: $51.32 (1.51% above spot)
  Expiration breakeven: $53.16  Resilience: 0.03
  Exits: 50% at $0.08, 25% at $0.12
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: BAC BULL_PUT exp 2026-11-27 (15 DTE)
  Mode: INCOME
  Overall score: 11/100 (POP Fit 72, M2M Distance 16, Credit Quality 32, Liquidity 0, Resilience 5)
  Leg: SELL Put $48.00 mid 0.21
  Leg: BUY Put $47.00 mid 0.12
  Spot $50.56  Credit $0.10  Width $1.00  POP 86%
  Early-red M2M flip: $49.71 (1.67% below spot)
  Expiration breakeven: $47.91  Resilience: 0.05
  Exits: 50% at $0.05, 25% at $0.07
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.