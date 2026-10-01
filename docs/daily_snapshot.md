# Grant Options Income System — Daily Snapshot

Generated: 2026-10-01 18:41 UTC (live data)
Generated (Pacific): Thursday, October 01, 2026 at 11:41 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- WMT: score 0.42, spot $104.74, near-ATM IV 23.1%, ATR $2.15

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-10-16 (15 DTE)
  Mode: INCOME
  Overall score: 17/100 (POP Fit 95, M2M Distance 15, Credit Quality 36, Liquidity 0, Resilience 10)
  Leg: SELL Put $101.00 mid 0.54
  Leg: BUY Put $98.00 mid 0.23
  Spot $104.74  Credit $0.32  Width $3.00  POP 81%
  Early-red M2M flip: $103.11 (1.56% below spot)
  Expiration breakeven: $100.68  Resilience: 0.10
  Exits: 50% at $0.16, 25% at $0.24
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: WMT BULL_PUT exp 2026-10-16 (15 DTE)
  Mode: INCOME
  Overall score: 16/100 (POP Fit 95, M2M Distance 15, Credit Quality 33, Liquidity 0, Resilience 8)
  Leg: SELL Put $101.00 mid 0.54
  Leg: BUY Put $97.00 mid 0.15
  Spot $104.74  Credit $0.40  Width $4.00  POP 81%
  Early-red M2M flip: $103.12 (1.54% below spot)
  Expiration breakeven: $100.60  Resilience: 0.08
  Exits: 50% at $0.20, 25% at $0.30
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.