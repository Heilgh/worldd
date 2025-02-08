import random
import math
from typing import List, Tuple

class Perlin:
    def __init__(self, seed=None):
        """Initialize Perlin noise generator"""
        try:
            # Convert seed to integer if it's not None
            if seed is not None:
                if isinstance(seed, (int, float)):
                    seed = int(seed)
                elif isinstance(seed, str):
                    # Use hash of string as seed
                    seed = hash(seed)
                elif isinstance(seed, (bytes, bytearray)):
                    # Convert bytes to integer
                    seed = int.from_bytes(seed, 'big')
                else:
                    # Default to random seed if type is unsupported
                    seed = random.randint(0, 1000000)
            
            random.seed(seed)
            self.permutation = list(range(256))
            random.shuffle(self.permutation)
            self.permutation += self.permutation
            
        except Exception as e:
            print(f"Error initializing Perlin noise: {e}")
            # Initialize with default values on error
            self.permutation = list(range(256)) * 2
        
    def noise2d(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise value"""
        try:
            # Ensure inputs are real numbers
            x = float(x)
            y = float(y)
            
            # Integer coordinates
            X = int(math.floor(x)) & 255
            Y = int(math.floor(y)) & 255
            
            # Relative coordinates
            x -= math.floor(x)
            y -= math.floor(y)
            
            # Fade curves
            u = self._fade(float(x))
            v = self._fade(float(y))
            
            # Hash coordinates
            A = self.permutation[X] + Y
            AA = self.permutation[A & 255]
            AB = self.permutation[(A + 1) & 255]
            B = self.permutation[(X + 1) & 255] + Y
            BA = self.permutation[B & 255]
            BB = self.permutation[(B + 1) & 255]
            
            # Blend results
            result = self._lerp(v,
                self._lerp(u,
                    self._grad(self.permutation[AA], x, y),
                    self._grad(self.permutation[BA], x - 1, y)
                ),
                self._lerp(u,
                    self._grad(self.permutation[AB], x, y - 1),
                    self._grad(self.permutation[BB], x - 1, y - 1)
                )
            )
            
            # Ensure result is a real number
            if isinstance(result, complex):
                return float(result.real)
            return float(result)
            
        except Exception as e:
            print(f"Error in noise2d: {e}")
            return 0.0
        
    def _fade(self, t: float) -> float:
        """Fade function"""
        try:
            t = float(t)
            return float(t * t * t * (t * (t * 6 - 15) + 10))
        except Exception as e:
            print(f"Error in _fade: {e}")
            return 0.0
        
    def _lerp(self, t: float, a: float, b: float) -> float:
        """Linear interpolation"""
        try:
            t, a, b = float(t), float(a), float(b)
            return float(a + t * (b - a))
        except Exception as e:
            print(f"Error in _lerp: {e}")
            return 0.0
        
    def _grad(self, hash: int, x: float, y: float) -> float:
        """Gradient function"""
        try:
            # Ensure inputs are real numbers
            x = float(x)
            y = float(y)
            h = int(hash & 15)  # Convert hash to 4-bit number
            
            # Use simpler gradient calculation to avoid complex numbers
            grad_x = 1.0 if h & 1 else -1.0
            grad_y = 1.0 if h & 2 else -1.0
            
            # Calculate dot product with input coordinates
            return float(grad_x * x + grad_y * y)
            
        except Exception as e:
            print(f"Error in _grad: {e}")
            return 0.0 