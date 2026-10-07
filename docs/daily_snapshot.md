# Grant Options Income System — Daily Snapshot

Generated: 2026-10-07 19:12 UTC (live data)
Generated (Pacific): Wednesday, October 07, 2026 at 12:12 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- WMT: score 0.40, spot $108.25, near-ATM IV 22.5%, ATR $2.21

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-10-23 (16 DTE)
  Mode: INCOME
  Overall score: 16/100 (POP Fit 88, M2M Distance 15, Credit Quality 39, Liquidity 0, Resilience 8)
  Leg: SELL Put $104.00 mid 0.54
  Leg: BUY Put $101.00 mid 0.18
  Spot $108.29  Credit $0.36  Width $3.00  POP 82%
  Early-red M2M flip: $106.59 (1.57% below spot)
  Expiration breakeven: $103.64  Resilience: 0.08
  Exits: 50% at $0.18, 25% at $0.27
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: WMT BULL_PUT exp 2026-10-23 (16 DTE)
  Mode: INCOME
  Overall score: 15/100 (POP Fit 88, M2M Distance 15, Credit Quality 34, Liquidity 0, Resilience 8)
  Leg: SELL Put $104.00 mid 0.54
  Leg: BUY Put $100.00 mid 0.14
  Spot $108.29  Credit $0.41  Width $4.00  POP 82%
  Early-red M2M flip: $106.59 (1.57% below spot)
  Expiration breakeven: $103.59  Resilience: 0.08
  Exits: 50% at $0.20, 25% at $0.30
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.