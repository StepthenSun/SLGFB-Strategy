import numpy as np
from scipy.linalg import expm, logm
import warnings

# Suppress mathematically trivial warnings (e.g., safe divide-by-zero handled in code)
warnings.filterwarnings('ignore')

class SE3Manifold:
    """
    Special Euclidean Group Manifold Engine (SE(3))
    Embeds market data (time, price, volume) into a curved geometric space.
    """
    def __init__(self, scale_factor: float = 1.0):
        self.scale_factor = scale_factor

    def price_to_algebra(self, log_returns: np.ndarray, volume_norm: np.ndarray, time_idx: np.ndarray) -> np.ndarray:
        """
        Maps market data to the Lie algebra se(3) using the Hat Map.
        xi_hat = [ 0  -θ  vx ]
                 [ θ   0  vy ]
                 [ 0   0   0 ]
        """
        n = len(log_returns)
        algebra = np.zeros((n, 3, 3))
        
        for i in range(n):
            # Rotational component (Price momentum)
            theta = np.arctan(log_returns[i] * self.scale_factor)
            # Translational component (Time and Volume)
            vx = time_idx[i] * self.scale_factor
            vy = np.log1p(abs(log_returns[i])) * volume_norm[i]
            
            xi = np.zeros((3, 3))
            xi[0, 1] = -theta
            xi[1, 0] = theta
            xi[0, 2] = vx
            xi[1, 2] = vy
            algebra[i] = xi
            
        return algebra

    def exponential(self, xi_hat: np.ndarray) -> np.ndarray:
        """Exponential Map: se(3) -> SE(3)"""
        return expm(xi_hat)

    def logarithm(self, g: np.ndarray) -> np.ndarray:
        """Logarithmic Map: SE(3) -> se(3)"""
        return logm(g)

    def geodesic_distance(self, g1: np.ndarray, g2: np.ndarray) -> float:
        """
        Computes the Geodesic Distance between two states on the manifold.
        d(g1, g2) = || log(g1^-1 * g2) ||_F
        """
        relative = np.linalg.inv(g1) @ g2
        log_rel = self.logarithm(relative)
        return np.sqrt(np.sum(log_rel ** 2))

class GeometricSignalDetector:
    """
    Geometric Signal Detector: Captures exogenous market forces (trends) 
    by measuring the geodesic deviation of price trajectories.
    """
    def __init__(self, manifold: SE3Manifold, geo_thresh: float = 2.0):
        self.manifold = manifold
        self.geo_thresh = geo_thresh

    def detect_geodesic_deviation(self, g_seq: np.ndarray, window: int = 20) -> np.ndarray:
        """Computes geodesic deviation based on the Jacobi Field."""
        n = len(g_seq)
        dev = np.zeros(n)
        
        for i in range(window, n):
            g_start, g_end = g_seq[i - window], g_seq[i]
            # Calculate the theoretical midpoint assuming no external forces (geodesic motion)
            log_dir = self.manifold.logarithm(np.linalg.inv(g_start) @ g_end)
            expected_mid = g_start @ self.manifold.exponential(0.5 * log_dir)
            # Actual observed midpoint
            actual_mid = g_seq[i - window // 2]
            # The deviation represents the exogenous force (Alpha signal)
            dev[i] = self.manifold.geodesic_distance(actual_mid, expected_mid)
            
        # Z-score normalization
        if np.std(dev) > 1e-10: 
            dev = dev / np.std(dev)
        return dev

    def generate_geometric_signals(self, price: np.ndarray, volume: np.ndarray) -> tuple:
        """Generates raw trading signals based on manifold geometry."""
        n = len(price)
        log_returns = np.diff(np.log(price), prepend=np.log(price[0]))
        vol_ma = np.convolve(volume, np.ones(20)/20, mode='same')
        vol_norm = volume / (vol_ma + 1e-10)
        time_idx = np.linspace(0, 1, n)
        
        # Embed onto manifold
        algebra = self.manifold.price_to_algebra(log_returns, vol_norm, time_idx)
        g_seq = np.array([self.manifold.exponential(xi) for xi in algebra])
        
        # Detect deviations and generate signals
        geo_dev = self.detect_geodesic_deviation(g_seq)
        signals = np.zeros(n, dtype=int)
        conf = np.zeros(n)
        
        for i in range(1, n):
            if abs(geo_dev[i]) > self.geo_thresh:
                # Trend-following directional signal
                signals[i] = 1 if log_returns[i] > 0 else -1
                conf[i] = min(abs(geo_dev[i]) / (self.geo_thresh * 2), 1.0)
                
        return signals, conf, {'algebra_sequence': algebra, 'g_sequence': g_seq}
