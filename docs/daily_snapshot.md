# Grant Options Income System — Daily Snapshot

Generated: 2026-09-15 22:30 UTC (live data)
Generated (Pacific): Tuesday, September 15, 2026 at 03:30 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: COMPRESSION
Decision: DEPLOY
Size multiplier: 1.00
  - SPX BB-width compressed: 0.0226 <= 50% of avg 0.0469

## Candidates
- TSLA: score 0.68, spot $356.58, near-ATM IV 41.9%, ATR $13.99
- AMZN: score 0.54, spot $248.42, near-ATM IV 30.6%, ATR $5.89

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-02 (17 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 89, M2M Distance 13, Credit Quality 72, Liquidity 70, Resilience 3)
  Leg: SELL Put $335.00 mid 4.67
  Leg: BUY Put $330.00 mid 3.60
  Spot $356.58  Credit $1.08  Width $5.00  POP 78%
  Early-red M2M flip: $347.47 (2.55% below spot)
  Expiration breakeven: $333.93  Resilience: 0.03
  Exits: 50% at $0.54, 25% at $0.81
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-02 (17 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 89, M2M Distance 13, Credit Quality 72, Liquidity 70, Resilience 3)
  Leg: SELL Put $335.00 mid 4.67
  Leg: BUY Put $330.00 mid 3.60
  Spot $356.58  Credit $1.08  Width $5.00  POP 78%
  Early-red M2M flip: $347.47 (2.55% below spot)
  Expiration breakeven: $333.93  Resilience: 0.03
  Exits: 50% at $0.54, 25% at $0.81
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: AMZN BEAR_CALL exp 2026-10-02 (17 DTE)
  Mode: INCOME
  Overall score: 22/100 (POP Fit 66, M2M Distance 12, Credit Quality 65, Liquidity 49, Resilience 3)
  Leg: SELL Call $260.00 mid 2.60
  Leg: BUY Call $265.00 mid 1.64
  Spot $248.42  Credit $0.97  Width $5.00  POP 73%
  Early-red M2M flip: $252.83 (1.77% above spot)
  Expiration breakeven: $260.97  Resilience: 0.03
  Exits: 50% at $0.48, 25% at $0.73
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: AMZN BEAR_CALL exp 2026-10-02 (17 DTE)
  Mode: INCOME
  Overall score: 22/100 (POP Fit 66, M2M Distance 12, Credit Quality 65, Liquidity 49, Resilience 3)
  Leg: SELL Call $260.00 mid 2.60
  Leg: BUY Call $265.00 mid 1.64
  Spot $248.42  Credit $0.97  Width $5.00  POP 73%
  Early-red M2M flip: $252.83 (1.77% above spot)
  Expiration breakeven: $260.97  Resilience: 0.03
  Exits: 50% at $0.48, 25% at $0.73
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.