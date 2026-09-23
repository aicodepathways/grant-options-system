# Grant Options Income System — Daily Snapshot

Generated: 2026-09-23 17:42 UTC (live data)
Generated (Pacific): Wednesday, September 23, 2026 at 10:42 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.62, spot $379.27, near-ATM IV 40.1%, ATR $13.40
- AMZN: score 0.55, spot $248.35, near-ATM IV 29.2%, ATR $5.53

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 35/100 (POP Fit 90, M2M Distance 14, Credit Quality 90, Liquidity 71, Resilience 3)
  Leg: SELL Put $357.50 mid 4.58
  Leg: BUY Put $355.00 mid 3.90
  Spot $379.10  Credit $0.67  Width $2.50  POP 78%
  Early-red M2M flip: $369.12 (2.63% below spot)
  Expiration breakeven: $356.82  Resilience: 0.03
  Exits: 50% at $0.34, 25% at $0.51
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 35/100 (POP Fit 90, M2M Distance 14, Credit Quality 90, Liquidity 71, Resilience 3)
  Leg: SELL Put $357.50 mid 4.58
  Leg: BUY Put $355.00 mid 3.90
  Spot $379.10  Credit $0.67  Width $2.50  POP 78%
  Early-red M2M flip: $369.12 (2.63% below spot)
  Expiration breakeven: $356.82  Resilience: 0.03
  Exits: 50% at $0.34, 25% at $0.51
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: AMZN BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 30/100 (POP Fit 92, M2M Distance 13, Credit Quality 66, Liquidity 66, Resilience 5)
  Leg: SELL Put $237.50 mid 2.16
  Leg: BUY Put $235.00 mid 1.67
  Spot $248.29  Credit $0.50  Width $2.50  POP 78%
  Early-red M2M flip: $243.88 (1.78% below spot)
  Expiration breakeven: $237.00  Resilience: 0.05
  Exits: 50% at $0.25, 25% at $0.37
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: AMZN BULL_PUT exp 2026-10-09 (16 DTE)
  Mode: INCOME
  Overall score: 30/100 (POP Fit 92, M2M Distance 13, Credit Quality 66, Liquidity 66, Resilience 5)
  Leg: SELL Put $237.50 mid 2.16
  Leg: BUY Put $235.00 mid 1.67
  Spot $248.29  Credit $0.50  Width $2.50  POP 78%
  Early-red M2M flip: $243.88 (1.78% below spot)
  Expiration breakeven: $237.00  Resilience: 0.05
  Exits: 50% at $0.25, 25% at $0.37
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.