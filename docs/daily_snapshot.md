# Grant Options Income System — Daily Snapshot

Generated: 2026-08-24 14:23 UTC (live data)
Generated (Pacific): Monday, August 24, 2026 at 07:23 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- QQQ: score 0.34, spot $704.54, near-ATM IV 19.3%, ATR $8.69

## Trade Proposals
### #1: QQQ BEAR_CALL exp 2026-09-11 (18 DTE)
  Mode: OPPORTUNITY
  Overall score: 25/100 (POP Fit 85, M2M Distance 11, Credit Quality 98, Liquidity 86, Resilience 2)
  Leg: SELL Call $720.00 mid 5.50
  Leg: BUY Call $725.00 mid 3.97
  Spot $704.51  Credit $1.53  Width $5.00  POP 68%
  Early-red M2M flip: $711.87 (1.04% above spot)
  Expiration breakeven: $721.52  Resilience: 0.02
  Exits: 50% at $0.76, 25% at $1.14
  Validation: VALID
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #2: QQQ BEAR_CALL exp 2026-09-11 (18 DTE)
  Mode: OPPORTUNITY
  Overall score: 25/100 (POP Fit 85, M2M Distance 11, Credit Quality 96, Liquidity 87, Resilience 2)
  Leg: SELL Call $720.00 mid 5.50
  Leg: BUY Call $724.00 mid 4.25
  Spot $704.51  Credit $1.25  Width $4.00  POP 68%
  Early-red M2M flip: $711.86 (1.04% above spot)
  Expiration breakeven: $721.25  Resilience: 0.02
  Exits: 50% at $0.62, 25% at $0.93
  Validation: VALID
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.