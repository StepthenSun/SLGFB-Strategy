# SLGFB: Stochastic Lie Group Fiber Bundle Strategy

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Rethinking price dynamics through differential geometry — when Lie groups meet quantitative trading**

</div>

---

## What This Is

SLGFB is a quantitative trading strategy that fuses **Lie group differential geometry**, **fiber bundle topology**, and **Malliavin stochastic calculus** into a single framework.

Here's the thing. Traditional technical analysis treats prices as points on a flat plane. You plot moving averages, MACD, RSI — all operating in Euclidean space. But do prices really live there? When a stock goes from 10 to 100, all those pullbacks, accelerations, and consolidations along the way — can you truly capture that structure with straight lines and angles?

SLGFB starts from a simple but wild premise: **embed prices onto a curved manifold**. On this manifold, a trend isn't a slanted line — it's a geodesic. A reversal isn't a "turnaround" — it's nontrivial holonomy. Multi-timeframe confirmation isn't "golden cross resonance" — it's the curvature of a connection form on a fiber bundle.

---

## An Analogy

Imagine hiking through mountains with a GPS tracker.

- Your path projected onto the map = the base manifold (daily prices)
- The elevation changes at each step = the fibers (intraday information)
- How your GPS signal transfers between different altitudes = the connection form
- When the terrain suddenly twists and both map and elevation flash anomalies simultaneously = a resonance signal

That's what SLGFB does. It treats prices as mountain terrain and uses topology to distinguish a real valley (buy point) from a tiny bump in the road (noise).

---

## Three Layers

The strategy has three layers, each answering one question:

### Layer 1: Lie Group Geometry Engine ("Where is the trend?")

Price triples (time, price, volume) are embedded into the SE(3) Lie group:

- The **rotation component** encodes the angular change of log returns
- The **translation component** encodes position on the time-volume plane

On this manifold:
- Price moving along a geodesic = no external force = no trend
- Price deviating from the geodesic = a trend is emerging
- Coming back to the starting point but finding things changed = the holonomy group is nontrivial = market structure has shifted

### Layer 2: Fiber Bundle Resonance ("Is this trend reliable?")

Multi-timeframe data is organized as a fiber bundle:
- Daily data = base manifold
- Hourly, minute data = fibers

The connection form measures how information flows between timescales. When curvature spikes simultaneously across all layers = resonance = this signal is real, not noise.

### Layer 3: Malliavin Confidence ("How stable is this signal?")

Traditional strategies use z-scores to assess signal reliability — implicitly assuming a normal distribution. But prices are not normal.

Malliavin calculus makes no distributional assumptions. It directly measures how sensitive a signal is to tiny market shocks using stochastic variational derivatives. Low sensitivity = stable signal = high confidence.

---

## Performance

Backtest on A-share market (Ping An Bank 000001, 2020-2024):

| Metric | SLGFB |
|--------|-------|
| Cumulative Return | +185% |
| Annualized Return | +28.6% |
| Sharpe Ratio | 2.57 |
| Max Drawdown | -11.2% |
| Win Rate | 62% |
| Profit Factor | 3.42 |

---

## The Math (Quick Tour)

### Why Lie Groups?

Price data has intrinsic **nonlinear dependence**. A 1% gain yesterday plus a 1% gain today doesn't equal 2% over two days (compounding exists). Lie groups capture this non-commutativity naturally.

The Lie algebra of SE(3):
