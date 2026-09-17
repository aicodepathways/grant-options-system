# Grant Options Income System — Daily Snapshot

Generated: 2026-09-17 17:27 UTC (live data)
Generated (Pacific): Thursday, September 17, 2026 at 10:27 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.67, spot $367.64, near-ATM IV 41.9%, ATR $14.46
- WMT: score 0.53, spot $106.75, near-ATM IV 22.8%, ATR $1.74
- AMZN: score 0.51, spot $251.19, near-ATM IV 29.4%, ATR $6.08
- MCD: score 0.30, spot $249.53, near-ATM IV 22.1%, ATR $3.87

## Trade Proposals
### #1: WMT BULL_PUT exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 32/100 (POP Fit 72, M2M Distance 16, Credit Quality 88, Liquidity 60, Resilience 12)
  Leg: SELL Put $104.00 mid 0.84
  Leg: BUY Put $103.00 mid 0.58
  Spot $106.75  Credit $0.26  Width $1.00  POP 74%
  Early-red M2M flip: $105.02 (1.61% below spot)
  Expiration breakeven: $103.73  Resilience: 0.12
  Exits: 50% at $0.13, 25% at $0.20
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 97, M2M Distance 13, Credit Quality 65, Liquidity 66, Resilience 3)
  Leg: SELL Put $345.00 mid 4.12
  Leg: BUY Put $340.00 mid 3.15
  Spot $367.71  Credit $0.97  Width $5.00  POP 79%
  Early-red M2M flip: $358.34 (2.55% below spot)
  Expiration breakeven: $344.02  Resilience: 0.03
  Exits: 50% at $0.49, 25% at $0.73
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: TSLA BULL_PUT exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 97, M2M Distance 13, Credit Quality 65, Liquidity 66, Resilience 3)
  Leg: SELL Put $345.00 mid 4.12
  Leg: BUY Put $340.00 mid 3.15
  Spot $367.71  Credit $0.97  Width $5.00  POP 79%
  Early-red M2M flip: $358.34 (2.55% below spot)
  Expiration breakeven: $344.02  Resilience: 0.03
  Exits: 50% at $0.49, 25% at $0.73
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: AMZN BEAR_CALL exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 98, M2M Distance 13, Credit Quality 48, Liquidity 59, Resilience 3)
  Leg: SELL Call $265.00 mid 1.69
  Leg: BUY Call $270.00 mid 0.96
  Spot $251.20  Credit $0.72  Width $5.00  POP 80%
  Early-red M2M flip: $255.46 (1.70% above spot)
  Expiration breakeven: $265.73  Resilience: 0.03
  Exits: 50% at $0.36, 25% at $0.54
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #5: AMZN BEAR_CALL exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 27/100 (POP Fit 98, M2M Distance 13, Credit Quality 48, Liquidity 59, Resilience 3)
  Leg: SELL Call $265.00 mid 1.69
  Leg: BUY Call $270.00 mid 0.96
  Spot $251.20  Credit $0.72  Width $5.00  POP 80%
  Early-red M2M flip: $255.46 (1.70% above spot)
  Expiration breakeven: $265.73  Resilience: 0.03
  Exits: 50% at $0.36, 25% at $0.54
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #6: WMT BULL_PUT exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 72, M2M Distance 15, Credit Quality 63, Liquidity 58, Resilience 10)
  Leg: SELL Put $104.00 mid 0.84
  Leg: BUY Put $101.00 mid 0.28
  Spot $106.75  Credit $0.56  Width $3.00  POP 74%
  Early-red M2M flip: $105.10 (1.54% below spot)
  Expiration breakeven: $103.44  Resilience: 0.10
  Exits: 50% at $0.28, 25% at $0.42
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #7: MCD BEAR_CALL exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 6/100 (POP Fit 97, M2M Distance 14, Credit Quality 38, Liquidity 0, Resilience 7)
  Leg: SELL Call $260.00 mid 1.14
  Leg: BUY Call $265.00 mid 0.57
  Spot $249.50  Credit $0.57  Width $5.00  POP 81%
  Early-red M2M flip: $252.98 (1.39% above spot)
  Expiration breakeven: $260.57  Resilience: 0.07
  Exits: 50% at $0.29, 25% at $0.43
  Validation: not run
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

### #8: MCD BEAR_CALL exp 2026-10-02 (15 DTE)
  Mode: INCOME
  Overall score: 6/100 (POP Fit 97, M2M Distance 14, Credit Quality 38, Liquidity 0, Resilience 7)
  Leg: SELL Call $260.00 mid 1.14
  Leg: BUY Call $265.00 mid 0.57
  Spot $249.50  Credit $0.57  Width $5.00  POP 81%
  Early-red M2M flip: $252.98 (1.39% above spot)
  Expiration breakeven: $260.57  Resilience: 0.07
  Exits: 50% at $0.29, 25% at $0.43
  Validation: not run
  Flags: M2M_TOO_CLOSE, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.