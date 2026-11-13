# Equity Derivatives Pricing, Volatility & Hedging

Front-office-oriented Python research: Black–Scholes vanilla pricing, numerical Greeks, Monte Carlo exotic options, 25-delta implied volatility diagnostics and discrete delta-hedging P&L under simulated scenarios.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python examples/run_demo.py
streamlit run app.py
```

Synthetic and optional public historical market data. Risk-neutral modeling is illustrative; delta-hedging is path dependent and incurs trading costs. Not a production-grade pricing model or investment advice.
