# Grant Options Income System — Daily Snapshot

Generated: 2026-08-26 14:22 UTC (live data)
Generated (Pacific): Wednesday, August 26, 2026 at 07:22 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- QQQ: score 0.38, spot $709.30, near-ATM IV 18.8%, ATR $7.90

## Trade Proposals
### #1: QQQ BEAR_CALL exp 2026-09-11 (16 DTE)
  Mode: OPPORTUNITY
  Overall score: 26/100 (POP Fit 89, M2M Distance 13, Credit Quality 90, Liquidity 87, Resilience 3)
  Leg: SELL Call $724.00 mid 5.80
  Leg: BUY Call $729.00 mid 4.16
  Spot $709.30  Credit $1.64  Width $5.00  POP 67%
  Early-red M2M flip: $717.31 (1.13% above spot)
  Expiration breakeven: $725.64  Resilience: 0.03
  Exits: 50% at $0.82, 25% at $1.23
  Validation: VALID
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #2: QQQ BEAR_CALL exp 2026-09-11 (16 DTE)
  Mode: OPPORTUNITY
  Overall score: 25/100 (POP Fit 89, M2M Distance 13, Credit Quality 83, Liquidity 87, Resilience 3)
  Leg: SELL Call $724.00 mid 5.80
  Leg: BUY Call $726.00 mid 5.11
  Spot $709.30  Credit $0.70  Width $2.00  POP 67%
  Early-red M2M flip: $717.35 (1.13% above spot)
  Expiration breakeven: $724.70  Resilience: 0.03
  Exits: 50% at $0.35, 25% at $0.52
  Validation: VALID
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.