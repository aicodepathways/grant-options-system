# Grant Options Income System — Daily Snapshot

Generated: 2026-09-14 18:20 UTC (live data)
Generated (Pacific): Monday, September 14, 2026 at 11:20 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: COMPRESSION
Decision: DEPLOY
Size multiplier: 1.00
  - SPX BB-width compressed: 0.0213 <= 50% of avg 0.0473

## Candidates
- TSLA: score 0.66, spot $361.00, near-ATM IV 40.2%, ATR $13.97
- WMT: score 0.44, spot $109.44, near-ATM IV 23.4%, ATR $1.87
- MCD: score 0.34, spot $257.42, near-ATM IV 22.7%, ATR $4.00

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-02 (18 DTE)
  Mode: INCOME
  Overall score: 30/100 (POP Fit 88, M2M Distance 12, Credit Quality 72, Liquidity 69, Resilience 3)
  Leg: SELL Put $340.00 mid 4.58
  Leg: BUY Put $335.00 mid 3.50
  Spot $361.01  Credit $1.08  Width $5.00  POP 78%
  Early-red M2M flip: $352.24 (2.43% below spot)
  Expiration breakeven: $338.93  Resilience: 0.03
  Exits: 50% at $0.54, 25% at $0.81
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-02 (18 DTE)
  Mode: INCOME
  Overall score: 30/100 (POP Fit 88, M2M Distance 12, Credit Quality 72, Liquidity 69, Resilience 3)
  Leg: SELL Put $340.00 mid 4.58
  Leg: BUY Put $335.00 mid 3.50
  Spot $361.01  Credit $1.08  Width $5.00  POP 78%
  Early-red M2M flip: $352.24 (2.43% below spot)
  Expiration breakeven: $338.93  Resilience: 0.03
  Exits: 50% at $0.54, 25% at $0.81
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: WMT BULL_PUT exp 2026-10-02 (18 DTE)
  Mode: INCOME
  Overall score: 15/100 (POP Fit 80, M2M Distance 13, Credit Quality 44, Liquidity 0, Resilience 8)
  Leg: SELL Put $106.00 mid 0.88
  Leg: BUY Put $101.00 mid 0.21
  Spot $109.44  Credit $0.67  Width $5.00  POP 76%
  Early-red M2M flip: $107.74 (1.55% below spot)
  Expiration breakeven: $105.33  Resilience: 0.08
  Exits: 50% at $0.33, 25% at $0.50
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: WMT BULL_PUT exp 2026-10-02 (18 DTE)
  Mode: INCOME
  Overall score: 12/100 (POP Fit 80, M2M Distance 12, Credit Quality 73, Liquidity 22, Resilience 5)
  Leg: SELL Put $106.00 mid 0.88
  Leg: BUY Put $105.00 mid 0.66
  Spot $109.44  Credit $0.22  Width $1.00  POP 76%
  Early-red M2M flip: $107.94 (1.37% below spot)
  Expiration breakeven: $105.78  Resilience: 0.05
  Exits: 50% at $0.11, 25% at $0.16
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #5: MCD BULL_PUT exp 2026-10-02 (18 DTE)
  Mode: INCOME
  Overall score: 7/100 (POP Fit 80, M2M Distance 13, Credit Quality 65, Liquidity 0, Resilience 7)
  Leg: SELL Put $250.00 mid 1.89
  Leg: BUY Put $245.00 mid 0.92
  Spot $257.42  Credit $0.97  Width $5.00  POP 76%
  Early-red M2M flip: $253.76 (1.42% below spot)
  Expiration breakeven: $249.03  Resilience: 0.07
  Exits: 50% at $0.49, 25% at $0.73
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #6: MCD BULL_PUT exp 2026-10-02 (18 DTE)
  Mode: INCOME
  Overall score: 7/100 (POP Fit 80, M2M Distance 13, Credit Quality 65, Liquidity 0, Resilience 7)
  Leg: SELL Put $250.00 mid 1.89
  Leg: BUY Put $245.00 mid 0.92
  Spot $257.42  Credit $0.97  Width $5.00  POP 76%
  Early-red M2M flip: $253.76 (1.42% below spot)
  Expiration breakeven: $249.03  Resilience: 0.07
  Exits: 50% at $0.49, 25% at $0.73
  Validation: INVALID (resilience 0.07 at or below hard-reject floor 0.10; builder flagged M2M_TOO_CLOSE at construction)
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.