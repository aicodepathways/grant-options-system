# Grant Options Income System — Daily Snapshot

Generated: 2026-11-28 00:26 UTC (live data)
Generated (Pacific): Friday, November 27, 2026 at 04:26 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: ELEVATED_VOL
Decision: DEPLOY
Size multiplier: 0.50
  - VIX 23.81 elevated (>20.0)

## Candidates
- LLY: score 0.55, spot $1392.38, near-ATM IV 35.7%, ATR $38.41
- WMT: score 0.42, spot $133.13, near-ATM IV 24.4%, ATR $2.58

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-12-18 (20 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 62, M2M Distance 17, Credit Quality 95, Liquidity 5, Resilience 22)
  Leg: SELL Put $129.00 mid 1.52
  Leg: BUY Put $128.00 mid 1.23
  Spot $133.13  Credit $0.29  Width $1.00  POP 72%
  Early-red M2M flip: $130.18 (2.22% below spot)
  Expiration breakeven: $128.72  Resilience: 0.22
  Exits: 50% at $0.14, 25% at $0.21
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: LLY BULL_PUT exp 2026-12-18 (20 DTE)
  Mode: INCOME
  Overall score: 23/100 (POP Fit 65, M2M Distance 11, Credit Quality 65, Liquidity 52, Resilience 8)
  Leg: SELL Put $1330.00 mid 21.83
  Leg: BUY Put $1325.00 mid 20.85
  Spot $1392.38  Credit $0.98  Width $5.00  POP 73%
  Early-red M2M flip: $1364.59 (2.00% below spot)
  Expiration breakeven: $1329.03  Resilience: 0.08
  Exits: 50% at $0.49, 25% at $0.73
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: LLY BULL_PUT exp 2026-12-18 (20 DTE)
  Mode: INCOME
  Overall score: 23/100 (POP Fit 65, M2M Distance 11, Credit Quality 65, Liquidity 52, Resilience 8)
  Leg: SELL Put $1330.00 mid 21.83
  Leg: BUY Put $1325.00 mid 20.85
  Spot $1392.38  Credit $0.98  Width $5.00  POP 73%
  Early-red M2M flip: $1364.59 (2.00% below spot)
  Expiration breakeven: $1329.03  Resilience: 0.08
  Exits: 50% at $0.49, 25% at $0.73
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: WMT BULL_PUT exp 2026-12-18 (20 DTE)
  Mode: INCOME
  Overall score: 20/100 (POP Fit 62, M2M Distance 12, Credit Quality 71, Liquidity 30, Resilience 5)
  Leg: SELL Put $129.00 mid 1.52
  Leg: BUY Put $126.00 mid 0.88
  Spot $133.13  Credit $0.64  Width $3.00  POP 72%
  Early-red M2M flip: $130.99 (1.60% below spot)
  Expiration breakeven: $128.36  Resilience: 0.05
  Exits: 50% at $0.32, 25% at $0.48
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.