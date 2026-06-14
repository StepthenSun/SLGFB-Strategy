import sys
import os
import pandas as pd
import numpy as np

# Append the parent directory to the system path to simulate package installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from slgfb import SLGFBSignalGenerator, SLGFBBacktest

def generate_synthetic_market_data(n=1000):
    """
    Generates a synthetic financial time series featuring trends and Brownian noise.
    (For live deployment, replace this with pd.read_csv to ingest real equities/crypto data).
    """
    dates = pd.date_range('2021-01-01', periods=n, freq='B')
    np.random.seed(42)
    
    # Construction: Sine wave cycles + upward drift + Gaussian white noise
    trend = np.sin(np.linspace(0, 15, n)) * 0.08
    drift = np.linspace(0, 0.5, n)
    noise = np.random.randn(n) * 0.02
    
    close_price = 100 * np.exp(trend + drift + noise)
    volume = np.random.randint(1_000_000, 10_000_000, n)
    
    return pd.DataFrame({'close': close_price, 'volume': volume}, index=dates)

if __name__ == "__main__":
    print("[1/4] Generating Market Data...")
    df = generate_synthetic_market_data(1000)
    
    print("[2/4] Initializing SLGFB Mathematical Engines...")
    generator = SLGFBSignalGenerator(
        scale_factor=1.5,           # Lie group manifold scaling factor
        resonance_threshold=0.75,   # Fiber bundle resonance threshold
        confidence_threshold=0.85   # Malliavin confidence requirement
    )
    
    print("[3/4] Computing Manifolds, Topologies & Stochastics...")
    # Core computation: Processing time depends on data size; underlying functions are Numba-accelerated
    signals, conf, diag = generator.generate(df['close'].values, df['volume'].values)
    
    print("[4/4] Executing Vectorized Backtest...")
    bt = SLGFBBacktest(initial_capital=100_000, commission=0.0003)
    bt.run(df, signals, conf, diag)
    
    # Output the analytical report and render charts
    bt.summary()
    bt.plot(save_path="slgfb_demo_dark.png")
