# Grant Options Income System — Daily Snapshot

Generated: 2026-09-10 22:01 UTC (live data)
Generated (Pacific): Thursday, September 10, 2026 at 03:01 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_CHOP
Decision: DEPLOY
Size multiplier: 1.00
  - SPX below slow SMA, no compression — benign chop

## Candidates
- TSLA: score 0.64, spot $363.56, near-ATM IV 39.5%, ATR $15.29
- AAPL: score 0.44, spot $326.57, near-ATM IV 26.1%, ATR $7.52

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-09-25 (15 DTE)
  Mode: INCOME
  Overall score: 29/100 (POP Fit 92, M2M Distance 13, Credit Quality 54, Liquidity 76, Resilience 3)
  Leg: SELL Put $340.00 mid 3.40
  Leg: BUY Put $335.00 mid 2.58
  Spot $363.56  Credit $0.82  Width $5.00  POP 82%
  Early-red M2M flip: $354.75 (2.42% below spot)
  Expiration breakeven: $339.19  Resilience: 0.03
  Exits: 50% at $0.41, 25% at $0.61
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-09-25 (15 DTE)
  Mode: INCOME
  Overall score: 29/100 (POP Fit 92, M2M Distance 13, Credit Quality 54, Liquidity 76, Resilience 3)
  Leg: SELL Put $340.00 mid 3.40
  Leg: BUY Put $335.00 mid 2.58
  Spot $363.56  Credit $0.82  Width $5.00  POP 82%
  Early-red M2M flip: $354.75 (2.42% below spot)
  Expiration breakeven: $339.19  Resilience: 0.03
  Exits: 50% at $0.41, 25% at $0.61
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: AAPL BULL_PUT exp 2026-09-25 (15 DTE)
  Mode: INCOME
  Overall score: 28/100 (POP Fit 85, M2M Distance 13, Credit Quality 65, Liquidity 61, Resilience 3)
  Leg: SELL Put $315.00 mid 2.63
  Leg: BUY Put $310.00 mid 1.66
  Spot $326.57  Credit $0.97  Width $5.00  POP 77%
  Early-red M2M flip: $321.46 (1.56% below spot)
  Expiration breakeven: $314.03  Resilience: 0.03
  Exits: 50% at $0.48, 25% at $0.73
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: AAPL BULL_PUT exp 2026-09-25 (15 DTE)
  Mode: INCOME
  Overall score: 28/100 (POP Fit 85, M2M Distance 13, Credit Quality 65, Liquidity 61, Resilience 3)
  Leg: SELL Put $315.00 mid 2.63
  Leg: BUY Put $310.00 mid 1.66
  Spot $326.57  Credit $0.97  Width $5.00  POP 77%
  Early-red M2M flip: $321.46 (1.56% below spot)
  Expiration breakeven: $314.03  Resilience: 0.03
  Exits: 50% at $0.48, 25% at $0.73
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.