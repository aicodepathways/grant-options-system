# Grant Options Income System — Daily Snapshot

Generated: 2026-09-22 17:31 UTC (live data)
Generated (Pacific): Tuesday, September 22, 2026 at 10:31 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.64, spot $378.53, near-ATM IV 41.6%, ATR $13.06
- AMZN: score 0.54, spot $254.15, near-ATM IV 29.3%, ATR $5.14

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-09 (17 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 97, M2M Distance 12, Credit Quality 68, Liquidity 67, Resilience 5)
  Leg: SELL Put $355.00 mid 4.28
  Leg: BUY Put $350.00 mid 3.25
  Spot $378.46  Credit $1.03  Width $5.00  POP 79%
  Early-red M2M flip: $368.96 (2.51% below spot)
  Expiration breakeven: $353.98  Resilience: 0.05
  Exits: 50% at $0.51, 25% at $0.77
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-09 (17 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 97, M2M Distance 12, Credit Quality 68, Liquidity 67, Resilience 5)
  Leg: SELL Put $355.00 mid 4.28
  Leg: BUY Put $350.00 mid 3.25
  Spot $378.46  Credit $1.03  Width $5.00  POP 79%
  Early-red M2M flip: $368.96 (2.51% below spot)
  Expiration breakeven: $353.98  Resilience: 0.05
  Exits: 50% at $0.51, 25% at $0.77
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: AMZN BULL_PUT exp 2026-10-09 (17 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 73, M2M Distance 13, Credit Quality 71, Liquidity 60, Resilience 7)
  Leg: SELL Put $245.00 mid 2.66
  Leg: BUY Put $240.00 mid 1.59
  Spot $254.02  Credit $1.07  Width $5.00  POP 75%
  Early-red M2M flip: $249.43 (1.81% below spot)
  Expiration breakeven: $243.93  Resilience: 0.07
  Exits: 50% at $0.54, 25% at $0.80
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: AMZN BULL_PUT exp 2026-10-09 (17 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 73, M2M Distance 13, Credit Quality 71, Liquidity 60, Resilience 7)
  Leg: SELL Put $245.00 mid 2.66
  Leg: BUY Put $240.00 mid 1.59
  Spot $254.02  Credit $1.07  Width $5.00  POP 75%
  Early-red M2M flip: $249.43 (1.81% below spot)
  Expiration breakeven: $243.93  Resilience: 0.07
  Exits: 50% at $0.54, 25% at $0.80
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.