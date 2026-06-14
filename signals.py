import numpy as np
from .geometry import SE3Manifold, GeometricSignalDetector
from .fiber import FiberBundleStructure
from .stochastic import MalliavinConfidence

class SLGFBSignalGenerator:
    """
    Core SLGFB Signal Generator.
    Executes a strict "three-layer mathematical protocol" to filter false breakouts.
    """
    def __init__(self, scale_factor=1.5, resonance_threshold=0.75, confidence_threshold=0.80):
        self.res_thresh = resonance_threshold
        self.conf_thresh = confidence_threshold
        
        # Initialize the three mathematical engines
        self.manifold = SE3Manifold(scale_factor)
        self.geom_detector = GeometricSignalDetector(self.manifold)
        self.fiber_bundle = FiberBundleStructure()
        self.malliavin = MalliavinConfidence()

    def generate(self, price: np.ndarray, volume: np.ndarray) -> tuple:
        n = len(price)
        
        # --- Layer 1: Lie Group Geometry (Trend Detection) ---
        geo_sigs, geo_conf, geo_diag = self.geom_detector.generate_geometric_signals(price, volume)
        
        # --- Layer 2: Fiber Topology (Multi-Timeframe Resonance) ---
        algebra = geo_diag['algebra_sequence']
        base_sec = algebra.reshape(n, -1)[:, :3]
        
        # (In live trading, real minute-level data should be passed here. 
        # Here we simulate micro-structure noise using randomized manifold perturbations)
        fiber1 = base_sec + np.random.randn(n, 3) * 0.02
        fiber2 = base_sec + np.random.randn(n, 3) * 0.01
        
        conn = self.fiber_bundle.compute_connection(base_sec, [fiber1, fiber2])
        base_curv = self.fiber_bundle.section_curvature(conn, base_sec)
        fiber_curvs = [self.fiber_bundle.section_curvature(conn, f) for f in [fiber1, fiber2]]
        
        resonance = self.fiber_bundle.detect_resonance(base_curv, fiber_curvs, self.res_thresh)
        
        # --- Layer 3: Malliavin Stochastic (Confidence Quantification) ---
        returns = np.diff(np.log(price), prepend=np.log(price[0]))
        vol = np.convolve(np.abs(returns), np.ones(20)/20, mode='same')
        mall_conf = self.malliavin.compute_confidence(geo_conf, vol)
        
        # --- Signal Fusion ---
        signals = np.zeros(n, dtype=int)
        final_conf = np.zeros(n)
        
        for i in range(n):
            # A valid signal MUST satisfy: Geometric Deviation + Topological Resonance + High Malliavin Confidence
            if geo_sigs[i] != 0 and resonance[i] > self.res_thresh and mall_conf[i] > self.conf_thresh:
                signals[i] = geo_sigs[i]
                final_conf[i] = (geo_conf[i] * resonance[i] * mall_conf[i]) ** (1/3)
                
        # Filter dense/clustered noise signals
        last_idx = -10
        for i in range(n):
            if signals[i] != 0:
                if i - last_idx < 10: 
                    signals[i] = 0
                else: 
                    last_idx = i
                
        diagnostics = {
            'resonance': resonance, 
            'malliavin_conf': mall_conf, 
            'base_curv': base_curv
        }
        return signals, final_conf, diagnostics
