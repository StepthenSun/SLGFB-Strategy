import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class SLGFBBacktest:
    """Professional Vectorized Backtesting Engine"""
    
    def __init__(self, initial_capital=1_000_000, commission=0.0003, slippage=0.0001):
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = None
        self.trades_count = 0

    def run(self, df: pd.DataFrame, signals: np.ndarray, conf: np.ndarray, diag: dict) -> pd.DataFrame:
        """Executes the event-driven logic in a vectorized-friendly loop."""
        close = df['close'].values
        n = len(close)
        
        equity = np.zeros(n)
        capital = self.capital
        position = 0
        shares = 0
        entry_price = 0
        
        for i in range(n):
            # Daily equity update
            if position == 1: 
                equity[i] = capital + shares * (close[i] - entry_price)
            elif position == -1: 
                equity[i] = capital + shares * (entry_price - close[i])
            else: 
                equity[i] = capital
            
            # Exit Logic: Reverse signal, or a sharp decay in geometric resonance
            if position != 0 and (signals[i] == -position or (i > 0 and diag['resonance'][i] < 0.3)):
                pnl = shares * (close[i] - entry_price) if position == 1 else shares * (entry_price - close[i])
                # Deduct slippage and commissions
                capital += pnl - (shares * close[i] * (self.commission + self.slippage))
                position = 0
                shares = 0
            
            # Entry Logic: Confidence dictates position sizing (modified Kelly Criterion)
            if position == 0 and signals[i] != 0:
                position = signals[i]
                entry_price = close[i]
                # Higher confidence -> Larger position size (Max 25% allocation)
                shares = int((capital * 0.25 * conf[i]) / entry_price)
                capital -= shares * entry_price * self.commission
                self.trades_count += 1
                
        self.results = pd.DataFrame({
            'equity': equity, 
            'close': close, 
            'signal': signals, 
            'resonance': diag['resonance']
        }, index=df.index)
        
        return self.results

    def summary(self):
        """Prints core quantitative performance metrics."""
        eq = self.results['equity'].values
        ret = (eq[-1] - self.capital) / self.capital
        peak = np.maximum.accumulate(eq)
        dd = np.min((eq - peak) / peak)
        print("="*40)
        print(" 🌌 SLGFB Backtest Summary")
        print("="*40)
        print(f" Total Return : {ret:>10.2%}")
        print(f" Max Drawdown : {dd:>10.2%}")
        print(f" Total Trades : {self.trades_count:>10}")
        print("="*40)

    def plot(self, save_path=None):
        """Renders publication-quality visualization charts."""
        # Use dark theme for a sophisticated, technical aesthetic
        plt.style.use('dark_background')
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 2, 1]})
        
        # 1. Equity Curve
        axes[0].plot(self.results.index, self.results['equity'], color='#00FFFF', linewidth=2)
        axes[0].set_title('SLGFB Portfolio Equity', fontsize=14, fontweight='bold', color='white')
        axes[0].grid(True, alpha=0.2)
        
        # 2. Price and Execution Points
        axes[1].plot(self.results.index, self.results['close'], color='#B0C4DE', alpha=0.8)
        buy = self.results['signal'] == 1
        sell = self.results['signal'] == -1
        axes[1].scatter(self.results.index[buy], self.results['close'][buy], c='#00FF00', marker='^', s=120, label='Buy', zorder=5)
        axes[1].scatter(self.results.index[sell], self.results['close'][sell], c='#FF0040', marker='v', s=120, label='Sell', zorder=5)
        axes[1].set_title('Market Price & SLGFB Execution Signals', fontsize=14, fontweight='bold', color='white')
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.2)
        
        # 3. Geometric Resonance Strength
        axes[2].fill_between(self.results.index, self.results['resonance'], color='#8A2BE2', alpha=0.5)
        axes[2].plot(self.results.index, self.results['resonance'], color='#9370DB', linewidth=1)
        axes[2].axhline(y=0.75, color='#FFD700', linestyle='--', linewidth=1.5, label='Resonance Threshold')
        axes[2].set_title('Fiber Bundle Geometric Resonance', fontsize=14, fontweight='bold', color='white')
        axes[2].legend(loc='upper left')
        axes[2].grid(True, alpha=0.2)
        
        plt.tight_layout()
        if save_path: 
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
            print(f"Chart successfully saved to -> {save_path}")
        plt.show()
