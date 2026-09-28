# Grant Options Income System — Daily Snapshot

Generated: 2026-09-28 22:58 UTC (live data)
Generated (Pacific): Monday, September 28, 2026 at 03:58 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.64, spot $357.45, near-ATM IV 40.3%, ATR $11.16
- GLD: score 0.42, spot $377.91, near-ATM IV 22.5%, ATR $7.37

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 71, M2M Distance 13, Credit Quality 85, Liquidity 73, Resilience 7)
  Leg: SELL Put $340.00 mid 5.50
  Leg: BUY Put $335.00 mid 4.22
  Spot $357.45  Credit $1.28  Width $5.00  POP 74%
  Early-red M2M flip: $348.19 (2.59% below spot)
  Expiration breakeven: $338.73  Resilience: 0.07
  Exits: 50% at $0.64, 25% at $0.96
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 71, M2M Distance 13, Credit Quality 85, Liquidity 73, Resilience 7)
  Leg: SELL Put $340.00 mid 5.50
  Leg: BUY Put $335.00 mid 4.22
  Spot $357.45  Credit $1.28  Width $5.00  POP 74%
  Early-red M2M flip: $348.19 (2.59% below spot)
  Expiration breakeven: $338.73  Resilience: 0.07
  Exits: 50% at $0.64, 25% at $0.96
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: GLD BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 13/100 (POP Fit 81, M2M Distance 10, Credit Quality 78, Liquidity 36, Resilience 0)
  Leg: SELL Put $366.00 mid 3.00
  Leg: BUY Put $365.00 mid 2.76
  Spot $377.91  Credit $0.24  Width $1.00  POP 76%
  Early-red M2M flip: $373.47 (1.17% below spot)
  Expiration breakeven: $365.76  Resilience: 0.00
  Exits: 50% at $0.12, 25% at $0.18
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #4: GLD BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 13/100 (POP Fit 81, M2M Distance 11, Credit Quality 73, Liquidity 34, Resilience 2)
  Leg: SELL Put $366.00 mid 3.00
  Leg: BUY Put $364.00 mid 2.56
  Spot $377.91  Credit $0.44  Width $2.00  POP 76%
  Early-red M2M flip: $373.11 (1.27% below spot)
  Expiration breakeven: $365.56  Resilience: 0.02
  Exits: 50% at $0.22, 25% at $0.33
  Validation: INVALID (resilience 0.02 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.