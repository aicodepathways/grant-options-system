# Grant Options Income System — Daily Snapshot

Generated: 2026-09-24 22:47 UTC (live data)
Generated (Pacific): Thursday, September 24, 2026 at 03:47 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.64, spot $377.94, near-ATM IV 41.1%, ATR $11.63
- AMZN: score 0.55, spot $249.38, near-ATM IV 30.0%, ATR $5.48

## Trade Proposals
### #1: AMZN BULL_PUT exp 2026-10-09 (15 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 85, M2M Distance 13, Credit Quality 72, Liquidity 39, Resilience 7)
  Leg: SELL Put $240.00 mid 2.15
  Leg: BUY Put $237.50 mid 1.61
  Spot $249.38  Credit $0.54  Width $2.50  POP 77%
  Early-red M2M flip: $244.82 (1.83% below spot)
  Expiration breakeven: $239.46  Resilience: 0.07
  Exits: 50% at $0.27, 25% at $0.41
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: AMZN BULL_PUT exp 2026-10-09 (15 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 85, M2M Distance 13, Credit Quality 72, Liquidity 39, Resilience 7)
  Leg: SELL Put $240.00 mid 2.15
  Leg: BUY Put $237.50 mid 1.61
  Spot $249.38  Credit $0.54  Width $2.50  POP 77%
  Early-red M2M flip: $244.82 (1.83% below spot)
  Expiration breakeven: $239.46  Resilience: 0.07
  Exits: 50% at $0.27, 25% at $0.41
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: TSLA BEAR_CALL exp 2026-10-09 (15 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 66, M2M Distance 11, Credit Quality 68, Liquidity 72, Resilience 2)
  Leg: SELL Call $400.00 mid 4.97
  Leg: BUY Call $405.00 mid 3.95
  Spot $377.94  Credit $1.02  Width $5.00  POP 73%
  Early-red M2M flip: $386.04 (2.14% above spot)
  Expiration breakeven: $401.02  Resilience: 0.02
  Exits: 50% at $0.51, 25% at $0.77
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: TSLA BEAR_CALL exp 2026-10-09 (15 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 66, M2M Distance 11, Credit Quality 68, Liquidity 72, Resilience 2)
  Leg: SELL Call $400.00 mid 4.97
  Leg: BUY Call $405.00 mid 3.95
  Spot $377.94  Credit $1.02  Width $5.00  POP 73%
  Early-red M2M flip: $386.04 (2.14% above spot)
  Expiration breakeven: $401.02  Resilience: 0.02
  Exits: 50% at $0.51, 25% at $0.77
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.