# Grant Options Income System — Daily Snapshot

Generated: 2026-11-10 20:12 UTC (live data)
Generated (Pacific): Tuesday, November 10, 2026 at 12:12 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- BAC: score 0.55, spot $50.72, near-ATM IV 25.3%, ATR $1.25

## Trade Proposals
### #1: BAC BEAR_CALL exp 2026-11-27 (17 DTE)
  Mode: INCOME
  Overall score: 18/100 (POP Fit 92, M2M Distance 13, Credit Quality 55, Liquidity 0, Resilience 3)
  Leg: SELL Call $53.00 mid 0.30
  Leg: BUY Call $54.00 mid 0.14
  Spot $50.69  Credit $0.16  Width $1.00  POP 78%
  Early-red M2M flip: $51.52 (1.62% above spot)
  Expiration breakeven: $53.16  Resilience: 0.03
  Exits: 50% at $0.08, 25% at $0.12
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: BAC BULL_PUT exp 2026-11-27 (17 DTE)
  Mode: INCOME
  Overall score: 15/100 (POP Fit 79, M2M Distance 16, Credit Quality 37, Liquidity 0, Resilience 10)
  Leg: SELL Put $48.00 mid 0.27
  Leg: BUY Put $47.00 mid 0.16
  Spot $50.69  Credit $0.11  Width $1.00  POP 84%
  Early-red M2M flip: $49.68 (2.01% below spot)
  Expiration breakeven: $47.89  Resilience: 0.10
  Exits: 50% at $0.06, 25% at $0.08
  Validation: INVALID (resilience 0.10 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.