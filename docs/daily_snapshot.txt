# Grant Options Income System — Daily Snapshot

Generated: 2026-10-20 17:46 UTC (live data)
Generated (Pacific): Tuesday, October 20, 2026 at 10:46 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- META: score 0.63, spot $690.37, near-ATM IV 52.4%, ATR $21.90
- WFC: score 0.48, spot $81.75, near-ATM IV 29.7%, ATR $2.05

## Trade Proposals
### #1: META BULL_PUT exp 2026-11-06 (17 DTE)
  Mode: INCOME
  Overall score: 34/100 (POP Fit 55, M2M Distance 12, Credit Quality 97, Liquidity 67, Resilience 5)
  Leg: SELL Put $655.00 mid 15.93
  Leg: BUY Put $650.00 mid 14.38
  Spot $690.92  Credit $1.55  Width $5.00  POP 71%
  Early-red M2M flip: $669.29 (3.13% below spot)
  Expiration breakeven: $653.45  Resilience: 0.05
  Exits: 50% at $0.78, 25% at $1.16
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

### #2: META BULL_PUT exp 2026-11-06 (17 DTE)
  Mode: INCOME
  Overall score: 34/100 (POP Fit 55, M2M Distance 12, Credit Quality 97, Liquidity 67, Resilience 5)
  Leg: SELL Put $655.00 mid 15.93
  Leg: BUY Put $650.00 mid 14.38
  Spot $690.92  Credit $1.55  Width $5.00  POP 71%
  Early-red M2M flip: $669.29 (3.13% below spot)
  Expiration breakeven: $653.45  Resilience: 0.05
  Exits: 50% at $0.78, 25% at $1.16
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: EARLY_RED_VULNERABLE

### #3: WFC BULL_PUT exp 2026-11-06 (17 DTE)
  Mode: INCOME
  Overall score: 24/100 (POP Fit 93, M2M Distance 17, Credit Quality 54, Liquidity 0, Resilience 22)
  Leg: SELL Put $78.00 mid 0.70
  Leg: BUY Put $76.00 mid 0.38
  Spot $81.75  Credit $0.32  Width $2.00  POP 79%
  Early-red M2M flip: $79.69 (2.52% below spot)
  Expiration breakeven: $77.67  Resilience: 0.22
  Exits: 50% at $0.16, 25% at $0.24
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: WFC BULL_PUT exp 2026-11-06 (17 DTE)
  Mode: INCOME
  Overall score: 21/100 (POP Fit 93, M2M Distance 18, Credit Quality 37, Liquidity 0, Resilience 25)
  Leg: SELL Put $78.00 mid 0.70
  Leg: BUY Put $74.00 mid 0.26
  Spot $81.75  Credit $0.44  Width $4.00  POP 79%
  Early-red M2M flip: $79.59 (2.64% below spot)
  Expiration breakeven: $77.56  Resilience: 0.25
  Exits: 50% at $0.22, 25% at $0.33
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.