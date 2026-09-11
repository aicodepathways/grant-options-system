# Grant Options Income System — Daily Snapshot

Generated: 2026-09-11 16:54 UTC (live data)
Generated (Pacific): Friday, September 11, 2026 at 09:54 AM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.62, spot $365.25, near-ATM IV 37.4%, ATR $14.27
- WMT: score 0.39, spot $106.56, near-ATM IV 22.2%, ATR $1.86

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 34/100 (POP Fit 100, M2M Distance 14, Credit Quality 70, Liquidity 73, Resilience 5)
  Leg: SELL Put $340.00 mid 4.35
  Leg: BUY Put $335.00 mid 3.30
  Spot $365.31  Credit $1.05  Width $5.00  POP 80%
  Early-red M2M flip: $355.28 (2.75% below spot)
  Expiration breakeven: $338.95  Resilience: 0.05
  Exits: 50% at $0.52, 25% at $0.79
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 34/100 (POP Fit 100, M2M Distance 14, Credit Quality 70, Liquidity 73, Resilience 5)
  Leg: SELL Put $340.00 mid 4.35
  Leg: BUY Put $335.00 mid 3.30
  Spot $365.31  Credit $1.05  Width $5.00  POP 80%
  Early-red M2M flip: $355.28 (2.75% below spot)
  Expiration breakeven: $338.95  Resilience: 0.05
  Exits: 50% at $0.52, 25% at $0.79
  Validation: INVALID (resilience 0.05 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: WMT BEAR_CALL exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 22/100 (POP Fit 53, M2M Distance 13, Credit Quality 73, Liquidity 46, Resilience 8)
  Leg: SELL Call $110.00 mid 0.96
  Leg: BUY Call $111.00 mid 0.74
  Spot $106.57  Credit $0.22  Width $1.00  POP 71%
  Early-red M2M flip: $108.28 (1.61% above spot)
  Expiration breakeven: $110.22  Resilience: 0.08
  Exits: 50% at $0.11, 25% at $0.16
  Validation: INVALID (resilience 0.08 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: WMT BULL_PUT exp 2026-09-25 (14 DTE)
  Mode: INCOME
  Overall score: 19/100 (POP Fit 98, M2M Distance 18, Credit Quality 31, Liquidity 0, Resilience 13)
  Leg: SELL Put $103.00 mid 0.56
  Leg: BUY Put $98.00 mid 0.10
  Spot $106.57  Credit $0.47  Width $5.00  POP 80%
  Early-red M2M flip: $104.69 (1.76% below spot)
  Expiration breakeven: $102.53  Resilience: 0.13
  Exits: 50% at $0.23, 25% at $0.35
  Validation: VALID
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.