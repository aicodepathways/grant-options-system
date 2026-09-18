# Grant Options Income System — Daily Snapshot

Generated: 2026-09-18 16:56 UTC (live data)
Generated (Pacific): Friday, September 18, 2026 at 09:56 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.65, spot $363.08, near-ATM IV 40.4%, ATR $14.21
- MCD: score 0.30, spot $249.72, near-ATM IV 22.8%, ATR $3.72

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-09 (21 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 88, M2M Distance 12, Credit Quality 78, Liquidity 73, Resilience 3)
  Leg: SELL Put $340.00 mid 5.12
  Leg: BUY Put $335.00 mid 3.95
  Spot $363.08  Credit $1.17  Width $5.00  POP 78%
  Early-red M2M flip: $353.38 (2.67% below spot)
  Expiration breakeven: $338.82  Resilience: 0.03
  Exits: 50% at $0.59, 25% at $0.88
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-09 (21 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 88, M2M Distance 12, Credit Quality 78, Liquidity 73, Resilience 3)
  Leg: SELL Put $340.00 mid 5.12
  Leg: BUY Put $335.00 mid 3.95
  Spot $363.08  Credit $1.17  Width $5.00  POP 78%
  Early-red M2M flip: $353.38 (2.67% below spot)
  Expiration breakeven: $338.82  Resilience: 0.03
  Exits: 50% at $0.59, 25% at $0.88
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: MCD BULL_PUT exp 2026-10-09 (21 DTE)
  Mode: INCOME
  Overall score: 21/100 (POP Fit 96, M2M Distance 13, Credit Quality 51, Liquidity 0, Resilience 13)
  Leg: SELL Put $240.00 mid 1.47
  Leg: BUY Put $235.00 mid 0.70
  Spot $249.72  Credit $0.77  Width $5.00  POP 81%
  Early-red M2M flip: $245.60 (1.65% below spot)
  Expiration breakeven: $239.24  Resilience: 0.13
  Exits: 50% at $0.38, 25% at $0.57
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: MCD BULL_PUT exp 2026-10-09 (21 DTE)
  Mode: INCOME
  Overall score: 21/100 (POP Fit 96, M2M Distance 13, Credit Quality 51, Liquidity 0, Resilience 13)
  Leg: SELL Put $240.00 mid 1.47
  Leg: BUY Put $235.00 mid 0.70
  Spot $249.72  Credit $0.77  Width $5.00  POP 81%
  Early-red M2M flip: $245.60 (1.65% below spot)
  Expiration breakeven: $239.24  Resilience: 0.13
  Exits: 50% at $0.38, 25% at $0.57
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.