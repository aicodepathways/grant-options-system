# Grant Options Income System — Daily Snapshot

Generated: 2026-09-11 22:04 UTC (live data)
Generated (Pacific): Friday, September 11, 2026 at 03:04 PM Pacific

Freshness note for the reader: this page refreshes several times each weekday morning, roughly 6:45 AM to noon Pacific. Exact times drift because the free scheduler queues jobs. If the date above is not today, today's first run has not completed yet; advise re-checking after 7:30 AM Pacific rather than treating it as a failure.

## Regime
Label: BENIGN_TREND
Decision: DEPLOY
Size multiplier: 1.00
  - SPX above slow SMA — benign trend

## Candidates
- TSLA: score 0.62, spot $365.44, near-ATM IV 37.2%, ATR $14.27
- WMT: score 0.40, spot $107.15, near-ATM IV 22.2%, ATR $1.90

## Trade Proposals
### #1: TSLA BULL_PUT exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 97, M2M Distance 13, Credit Quality 63, Liquidity 72, Resilience 3)
  Leg: SELL Put $340.00 mid 4.15
  Leg: BUY Put $335.00 mid 3.20
  Spot $365.44  Credit $0.95  Width $5.00  POP 81%
  Early-red M2M flip: $355.88 (2.62% below spot)
  Expiration breakeven: $339.05  Resilience: 0.03
  Exits: 50% at $0.48, 25% at $0.71
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #2: TSLA BULL_PUT exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 31/100 (POP Fit 97, M2M Distance 13, Credit Quality 63, Liquidity 72, Resilience 3)
  Leg: SELL Put $340.00 mid 4.15
  Leg: BUY Put $335.00 mid 3.20
  Spot $365.44  Credit $0.95  Width $5.00  POP 81%
  Early-red M2M flip: $355.88 (2.62% below spot)
  Expiration breakeven: $339.05  Resilience: 0.03
  Exits: 50% at $0.48, 25% at $0.71
  Validation: INVALID (resilience 0.03 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #3: WMT BULL_PUT exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 26/100 (POP Fit 70, M2M Distance 17, Credit Quality 87, Liquidity 0, Resilience 23)
  Leg: SELL Put $104.00 mid 0.96
  Leg: BUY Put $103.00 mid 0.70
  Spot $107.15  Credit $0.26  Width $1.00  POP 74%
  Early-red M2M flip: $104.94 (2.06% below spot)
  Expiration breakeven: $103.74  Resilience: 0.23
  Exits: 50% at $0.13, 25% at $0.20
  Validation: INVALID (resilience 0.10 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

### #4: WMT BULL_PUT exp 2026-10-02 (21 DTE)
  Mode: INCOME
  Overall score: 19/100 (POP Fit 70, M2M Distance 15, Credit Quality 69, Liquidity 0, Resilience 10)
  Leg: SELL Put $104.00 mid 0.96
  Leg: BUY Put $101.00 mid 0.34
  Spot $107.15  Credit $0.62  Width $3.00  POP 74%
  Early-red M2M flip: $105.27 (1.75% below spot)
  Expiration breakeven: $103.38  Resilience: 0.10
  Exits: 50% at $0.31, 25% at $0.46
  Validation: INVALID (resilience 0.10 at or below hard-reject floor 0.10)
  Flags: M2M_WARN, EARLY_RED_VULNERABLE

## Notes for the AI advisor
- INCOME mode = conservative spec (wide strikes, 70-90% POP).
- OPPORTUNITY mode = the client's low-vol SPX style (strikes near half the expected move, credit 30-50% of width, POP floor ~55%). Index products only, VIX under 18.
- Early-red M2M flip = price where the trade is down 25% of credit 5 days after entry. The primary risk number.
- Full system documentation: README.md at the repo root.