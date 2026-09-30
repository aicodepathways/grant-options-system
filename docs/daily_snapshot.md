# Grant Options Income System — Daily Snapshot

Generated: 2026-09-30 23:16 UTC (live data)
Generated (Pacific): Wednesday, September 30, 2026 at 04:16 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- WMT: score 0.46, spot $103.92, near-ATM IV 25.8%, ATR $2.15

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-10-16 (16 DTE)
  Mode: INCOME
  Overall score: 42/100 (POP Fit 99, M2M Distance 22, Credit Quality 50, Liquidity 0, Resilience 75)
  Leg: SELL Put $100.00 mid 0.62
  Leg: BUY Put $99.00 mid 0.47
  Spot $103.92  Credit $0.15  Width $1.00  POP 80%
  Early-red M2M flip: $101.18 (2.63% below spot)
  Expiration breakeven: $99.85  Resilience: 0.75
  Exits: 50% at $0.08, 25% at $0.11
  Validation: VALID
  Flags: M2M_WARN

### #2: WMT BULL_PUT exp 2026-10-16 (16 DTE)
  Mode: INCOME
  Overall score: 37/100 (POP Fit 99, M2M Distance 21, Credit Quality 28, Liquidity 0, Resilience 73)
  Leg: SELL Put $100.00 mid 0.62
  Leg: BUY Put $98.00 mid 0.46
  Spot $103.92  Credit $0.16  Width $2.00  POP 80%
  Early-red M2M flip: $101.32 (2.50% below spot)
  Expiration breakeven: $99.83  Resilience: 0.73
  Exits: 50% at $0.08, 25% at $0.12
  Validation: VALID
  Flags: M2M_WARN

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.