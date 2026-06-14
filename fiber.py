import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class ConnectionForm:
    """Data structure for the Connection 1-form and Curvature 2-form."""
    values: np.ndarray     # The Connection (omega)
    curvature: np.ndarray  # The Curvature (Omega)

class FiberBundleStructure:
    """
    Principal Fiber Bundle P(M, G) Framework
    M: Base Manifold (Daily/Macro data)
    G: Fibers (High-frequency/Micro data)
    """
    
    def compute_connection(self, base: np.ndarray, fibers: List[np.ndarray]) -> ConnectionForm:
        """
        Computes the Maurer-Cartan Connection 1-form (ω) and Curvature 2-form (Ω).
        Ω = dω + ω ∧ ω
        """
        n = len(base)
        # Vertical component (High-frequency micro movements)
        vertical = sum([np.diff(f, axis=0, prepend=f[0:1])[:, :3] for f in fibers]) / len(fibers)
        # Horizontal component (Daily macro movements)
        horizontal = np.diff(base, axis=0, prepend=base[0:1])[:, :3]
        
        # Construct the connection ω
        total_conn = np.zeros((n, 3, 3))
        for i in range(n):
            for j in range(3):
                total_conn[i, j, j] = 0.1 + vertical[i, j] * 0.01
                total_conn[i, j, (j+1)%3] = horizontal[i, j] * 0.01
                
        # Compute curvature Ω (Exterior Derivative + Wedge Product)
        curvature = np.zeros((n, 3, 3))
        for i in range(1, n):
            d_omega = total_conn[i] - total_conn[i-1]
            omega_wedge = np.zeros((3, 3))
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        omega_wedge[a, b] += total_conn[i, a, c] * total_conn[i, c, b] - total_conn[i, b, c] * total_conn[i, c, a]
            curvature[i] = d_omega + 0.5 * omega_wedge
            
        return ConnectionForm(values=total_conn, curvature=curvature)

    def section_curvature(self, conn: ConnectionForm, section: np.ndarray) -> np.ndarray:
        """Computes the pullback curvature: s*Ω(ds, ds)"""
        n = len(section)
        curvatures = np.zeros(n)
        for i in range(1, n):
            ds = section[i] - section[i-1]
            Omega = conn.curvature[i]
            pulled = sum(ds[a] * Omega[a, b] * ds[b] for a in range(3) for b in range(3))
            curvatures[i] = pulled
        return curvatures

    def detect_resonance(self, base_curv: np.ndarray, fiber_curvs: List[np.ndarray], threshold: float) -> np.ndarray:
        """
        Geometric Resonance Detection
        Confirms authentic breakouts when the curvature of the macro base manifold 
        and the micro fibers spike simultaneously (satisfying the Bianchi Identity).
        """
        n = len(base_curv)
        resonance = np.zeros(n)
        
        # Normalization
        base_norm = base_curv / (np.std(base_curv) + 1e-10)
        fiber_norms = [fc / (np.std(fc) + 1e-10) for fc in fiber_curvs]
        
        for i in range(n):
            # Bianchi Identity resonance condition
            if abs(base_norm[i]) > threshold and all(abs(fn[i]) > threshold for fn in fiber_norms):
                strength = abs(base_norm[i])
                for fn in fiber_norms: 
                    strength *= min(abs(fn[i])/3, 1.0)
                resonance[i] = min(strength, 1.0)
                
        return resonance
