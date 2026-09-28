# Grant Options Income System — Daily Snapshot

Generated: 2026-09-28 19:59 UTC (live data)
Generated (Pacific): Monday, September 28, 2026 at 12:59 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.65, spot $357.74, near-ATM IV 40.4%, ATR $11.16
- GLD: score 0.42, spot $377.99, near-ATM IV 22.8%, ATR $7.37

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 72, M2M Distance 12, Credit Quality 85, Liquidity 85, Resilience 3)
  Leg: SELL Put $340.00 mid 5.40
  Leg: BUY Put $335.00 mid 4.12
  Spot $357.78  Credit $1.28  Width $5.00  POP 74%
  Early-red M2M flip: $349.07 (2.44% below spot)
  Expiration breakeven: $338.73  Resilience: 0.03
  Exits: 50% at $0.64, 25% at $0.96
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 72, M2M Distance 12, Credit Quality 85, Liquidity 85, Resilience 3)
  Leg: SELL Put $340.00 mid 5.40
  Leg: BUY Put $335.00 mid 4.12
  Spot $357.78  Credit $1.28  Width $5.00  POP 74%
  Early-red M2M flip: $349.07 (2.44% below spot)
  Expiration breakeven: $338.73  Resilience: 0.03
  Exits: 50% at $0.64, 25% at $0.96
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: GLD BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 16/100 (POP Fit 86, M2M Distance 11, Credit Quality 68, Liquidity 53, Resilience 3)
  Leg: SELL Put $366.00 mid 2.75
  Leg: BUY Put $365.00 mid 2.54
  Spot $377.98  Credit $0.21  Width $1.00  POP 77%
  Early-red M2M flip: $373.23 (1.26% below spot)
  Expiration breakeven: $365.80  Resilience: 0.03
  Exits: 50% at $0.10, 25% at $0.15
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #4: GLD BULL_PUT exp 2026-10-16 (18 DTE)
  Mode: INCOME
  Overall score: 16/100 (POP Fit 86, M2M Distance 11, Credit Quality 67, Liquidity 53, Resilience 3)
  Leg: SELL Put $366.00 mid 2.75
  Leg: BUY Put $364.00 mid 2.34
  Spot $377.98  Credit $0.40  Width $2.00  POP 77%
  Early-red M2M flip: $373.12 (1.28% below spot)
  Expiration breakeven: $365.60  Resilience: 0.03
  Exits: 50% at $0.20, 25% at $0.30
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.