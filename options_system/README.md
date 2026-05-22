# options_system — Phase 1

Rules-based, premium-selling options income pipeline.

```
regime_engine -> scanner -> trade_builder -> validator -> execution
```

## Quick start

```bash
pip install -r options_system/requirements.txt

# Run today's full pipeline (live):
python -m options_system.main

# Show top 3 cards, skip the real-time validator (research mode):
python -m options_system.main --top 3 --no-validate

# Backtest a window (uses synthetic chains — read the warning in output):
python -m options_system.main --backtest 2024-01-01 2024-06-30

# Launch the Streamlit dashboard:
streamlit run options_system/dashboard/app.py

# Run unit tests:
pytest options_system/tests
```

## Dashboard

Four pages under [options_system/dashboard/](options_system/dashboard/):

1. **Overview** ([app.py](options_system/dashboard/app.py)) — landing page; pipeline status, regime banner, quick stats.
2. **Regime Overview** ([1_Regime_Overview.py](options_system/dashboard/pages/1_Regime_Overview.py)) — VIX/SPX charts with band overlays, classifier reasoning, deployment map.
3. **Today's Candidates** ([2_Today's_Candidates.py](options_system/dashboard/pages/2_Today's_Candidates.py)) — ranked, color-coded table of all proposals; filters; jump to trade detail.
4. **Trade Detail** ([3_Trade_Detail.py](options_system/dashboard/pages/3_Trade_Detail.py)) — full execution card, validation status, failure-logic flags, exit ladder, copy-paste text card.
5. **Log Viewer** ([4_Log_Viewer.py](options_system/dashboard/pages/4_Log_Viewer.py)) — searchable history of past scans, decisions, trades.

Pipeline runs are cached per Streamlit session; click *Refresh data* in the sidebar to re-run. Every refresh also writes structured logs the Log Viewer can browse.

## Module map

| Module | Purpose |
| --- | --- |
| `data/` | Abstract `MarketDataAdapter`, yfinance impl, TTL cache, BSM greeks |
| `regime_engine/` | VIX/SPX rules, DEPLOY/NO-TRADE gate |
| `scanner/` | Universe filter — IV, liquidity, compression |
| `trade_builder/` | Strike selection, credit, POP, M2M flip, exits, ranking |
| `validator/` | Pre-entry refetch + drift / regime / liquidity check |
| `failure_logic/` | Pre-trade rejects + post-entry exit signals |
| `execution/` | Robinhood-friendly trade card |
| `logging_system/` | JSONL streams + daily summary |
| `backtester/` | Walk-forward backtest with synthetic chain generator |
| `config/` | All tunable thresholds (YAML) |
| `main.py` | Daily orchestrator + backtest entrypoint |

## Configs

All thresholds live in `config/*.yaml`. Edit them; nothing is hardcoded.

- `strategy_rules.yaml` — POP band, DTE window, buffer multipliers, exit ladder, ranking weights.
- `regime_config.yaml` — VIX bands, SPX trend / breakout / compression rules, deploy table.
- `failure_logic.yaml` — loss tolerance, M2M proximity, gamma zones, structure-break rules.
- `scanner_config.yaml` — universe, IV filters, liquidity, compression thresholds.
- `data_config.yaml` — provider choice, cache TTLs, retry behavior.

## Approximation warnings

- yfinance does not return option greeks consistently; we estimate them via Black-Scholes.
- The backtester's option chains are **synthetic** — Black-Scholes priced off a realized-vol IV proxy with a small term-structure tilt. No skew. Treat backtest absolute returns as indicative only. Swap `BlackScholesChainSource` for a real historical provider (Polygon, CBOE Datashop) by implementing `SyntheticChainSource`.
