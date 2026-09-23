# Grant Options Income System — Daily Snapshot

Generated: 2026-09-23 22:31 UTC (live data)
Generated (Pacific): Wednesday, September 23, 2026 at 03:31 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.62, spot $380.12, near-ATM IV 40.7%, ATR $13.02
- AMZN: score 0.55, spot $249.27, near-ATM IV 29.3%, ATR $5.45

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 82, M2M Distance 12, Credit Quality 83, Liquidity 73, Resilience 3)
  Leg: SELL Put $360.00 mid 4.97
  Leg: BUY Put $357.50 mid 4.35
  Spot $380.12  Credit $0.62  Width $2.50  POP 76%
  Early-red M2M flip: $371.17 (2.36% below spot)
  Expiration breakeven: $359.38  Resilience: 0.03
  Exits: 50% at $0.31, 25% at $0.47
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 82, M2M Distance 12, Credit Quality 83, Liquidity 73, Resilience 3)
  Leg: SELL Put $360.00 mid 4.97
  Leg: BUY Put $357.50 mid 4.35
  Spot $380.12  Credit $0.62  Width $2.50  POP 76%
  Early-red M2M flip: $371.17 (2.36% below spot)
  Expiration breakeven: $359.38  Resilience: 0.03
  Exits: 50% at $0.31, 25% at $0.47
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: AMZN BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 78, M2M Distance 13, Credit Quality 75, Liquidity 42, Resilience 5)
  Leg: SELL Put $240.00 mid 2.46
  Leg: BUY Put $237.50 mid 1.90
  Spot $249.27  Credit $0.56  Width $2.50  POP 76%
  Early-red M2M flip: $244.89 (1.76% below spot)
  Expiration breakeven: $239.44  Resilience: 0.05
  Exits: 50% at $0.28, 25% at $0.42
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: AMZN BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 78, M2M Distance 13, Credit Quality 75, Liquidity 42, Resilience 5)
  Leg: SELL Put $240.00 mid 2.46
  Leg: BUY Put $237.50 mid 1.90
  Spot $249.27  Credit $0.56  Width $2.50  POP 76%
  Early-red M2M flip: $244.89 (1.76% below spot)
  Expiration breakeven: $239.44  Resilience: 0.05
  Exits: 50% at $0.28, 25% at $0.42
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.