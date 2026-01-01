# backend/services/variation_engine.py
"""
Variation Engine
Intelligently mutates DNA parameters to create interesting variations
"""

import random
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class DNAParameters:
    """DNA parameters for a pattern"""
    density: float  # 0.0 - 1.0
    complexity: float  # 0.0 - 1.0
    groove: float  # 0.0 - 1.0
    evolution: float  # 0.0 - 1.0
    bars: int


class VariationEngine:
    """
    Generate variations of patterns by intelligently mutating DNA parameters

    Strategies:
    - Subtle: Small changes (±5-10%)
    - Moderate: Medium changes (±10-20%)
    - Extreme: Large changes (±20-40%)
    """

    def __init__(self, seed: int = None):
        """
        Initialize variation engine

        Args:
            seed: Random seed for reproducible variations
        """
        if seed is not None:
            random.seed(seed)

    def generate_variation(
        self,
        original: DNAParameters,
        strategy: str = 'moderate',
        preserve_feel: bool = True
    ) -> Tuple[DNAParameters, Dict[str, float]]:
        """
        Generate a variation of the original DNA parameters

        Args:
            original: Original DNA parameters
            strategy: 'subtle', 'moderate', or 'extreme'
            preserve_feel: If True, keeps groove and evolution closer to original

        Returns:
            Tuple of (new DNA parameters, parameter deltas)
        """
        # Define mutation ranges based on strategy
        ranges = {
            'subtle': (0.05, 0.10),      # 5-10% change
            'moderate': (0.10, 0.20),    # 10-20% change
            'extreme': (0.20, 0.40)      # 20-40% change
        }

        min_change, max_change = ranges.get(strategy, ranges['moderate'])

        # Generate parameter deltas
        deltas = {}

        # Density: Can vary freely
        deltas['density'] = self._generate_delta(
            original.density,
            min_change=min_change,
            max_change=max_change
        )

        # Complexity: Can vary freely
        deltas['complexity'] = self._generate_delta(
            original.complexity,
            min_change=min_change,
            max_change=max_change
        )

        # Groove: Preserve if requested (smaller changes)
        if preserve_feel:
            deltas['groove'] = self._generate_delta(
                original.groove,
                min_change=min_change * 0.5,
                max_change=max_change * 0.5
            )
        else:
            deltas['groove'] = self._generate_delta(
                original.groove,
                min_change=min_change,
                max_change=max_change
            )

        # Evolution: Preserve if requested (smaller changes)
        if preserve_feel:
            deltas['evolution'] = self._generate_delta(
                original.evolution,
                min_change=min_change * 0.5,
                max_change=max_change * 0.5
            )
        else:
            deltas['evolution'] = self._generate_delta(
                original.evolution,
                min_change=min_change,
                max_change=max_change
            )

        # Bars: Rarely change, and only for moderate/extreme
        if strategy in ['moderate', 'extreme'] and random.random() < 0.3:
            # Occasionally double or halve bars
            if original.bars >= 4 and random.random() < 0.5:
                deltas['bars'] = -original.bars // 2  # Halve
            elif original.bars < 8:
                deltas['bars'] = original.bars  # Double
            else:
                deltas['bars'] = 0
        else:
            deltas['bars'] = 0

        # Apply deltas to create new parameters
        new_params = DNAParameters(
            density=self._clamp(original.density + deltas['density']),
            complexity=self._clamp(original.complexity + deltas['complexity']),
            groove=self._clamp(original.groove + deltas['groove']),
            evolution=self._clamp(original.evolution + deltas['evolution']),
            bars=max(1, min(16, original.bars + deltas['bars']))
        )

        return new_params, deltas

    def generate_multiple_variations(
        self,
        original: DNAParameters,
        count: int = 3,
        strategy: str = 'moderate'
    ) -> list[Tuple[DNAParameters, Dict[str, float]]]:
        """
        Generate multiple variations at once

        Args:
            original: Original DNA parameters
            count: Number of variations to generate
            strategy: Mutation strategy

        Returns:
            List of (variation, deltas) tuples
        """
        variations = []
        for i in range(count):
            # Alternate preserve_feel to get diverse results
            preserve_feel = (i % 2 == 0)
            variation, deltas = self.generate_variation(
                original,
                strategy=strategy,
                preserve_feel=preserve_feel
            )
            variations.append((variation, deltas))

        return variations

    def generate_progressive_variations(
        self,
        original: DNAParameters,
        count: int = 5
    ) -> list[Tuple[DNAParameters, Dict[str, float]]]:
        """
        Generate progressively more extreme variations

        Useful for finding the "sweet spot" between original and extreme

        Args:
            original: Original DNA parameters
            count: Number of variations (default 5)

        Returns:
            List of variations from subtle to extreme
        """
        strategies = ['subtle', 'subtle', 'moderate', 'moderate', 'extreme']
        variations = []

        for i in range(min(count, len(strategies))):
            variation, deltas = self.generate_variation(
                original,
                strategy=strategies[i],
                preserve_feel=(i < 2)  # Preserve feel for first 2
            )
            variations.append((variation, deltas))

        return variations

    def _generate_delta(
        self,
        current_value: float,
        min_change: float,
        max_change: float
    ) -> float:
        """
        Generate a random delta within range, biased to avoid extremes

        Args:
            current_value: Current parameter value (0.0-1.0)
            min_change: Minimum change amount
            max_change: Maximum change amount

        Returns:
            Delta value (can be positive or negative)
        """
        # Random magnitude within range
        magnitude = random.uniform(min_change, max_change)

        # Random direction (positive or negative)
        direction = random.choice([-1, 1])

        delta = magnitude * direction

        # Bias away from edges (don't want to hit 0.0 or 1.0 too often)
        new_value = current_value + delta
        if new_value < 0.1 or new_value > 0.9:
            # Flip direction if too close to edge
            delta = -delta

        return delta

    def _clamp(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))

    def suggest_variation_type(self, track_type: str) -> str:
        """
        Suggest which parameters to focus on based on track type

        Args:
            track_type: 'drums', 'bass', 'melody', 'chords', 'fx'

        Returns:
            Suggestion text
        """
        suggestions = {
            'drums': 'Try varying density for more/fewer hits, or complexity for different patterns',
            'bass': 'Try varying groove for different feel, or evolution for more/less movement',
            'melody': 'Try varying complexity for different note patterns, or evolution for melodic development',
            'chords': 'Try varying density for rhythm changes, or complexity for chord voicings',
            'fx': 'Try extreme variations for completely different textures'
        }

        return suggestions.get(track_type, 'Experiment with different strategies!')


# Convenience functions

def create_variation(
    density: float,
    complexity: float,
    groove: float,
    evolution: float,
    bars: int,
    strategy: str = 'moderate'
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Create a variation from individual parameters

    Returns:
        Tuple of (new parameters dict, deltas dict)
    """
    engine = VariationEngine()
    original = DNAParameters(density, complexity, groove, evolution, bars)
    new_params, deltas = engine.generate_variation(original, strategy=strategy)

    return (
        {
            'density': new_params.density,
            'complexity': new_params.complexity,
            'groove': new_params.groove,
            'evolution': new_params.evolution,
            'bars': new_params.bars
        },
        deltas
    )
