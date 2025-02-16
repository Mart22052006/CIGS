"""
Manages different types of interaction scenarios for the bot.
"""

from typing import Dict, Any

from . import neutral_scenarios
from . import hostile_scenarios
from . import friendly_scenarios
from .csv_scenarios import neutral_scenarios as neutral_csv_scenarios
from .csv_scenarios import friendly_scenarios as friendly_csv_scenarios
from .csv_scenarios import high_probability_scenarios


class ScenarioManager:
    """Manages different types of interaction scenarios."""

    def __init__(self):
        """Initialize the scenario manager with all available scenarios."""
        self.scenarios = {
            "friendly": {
                **friendly_scenarios,
                **friendly_csv_scenarios.friendly_csv_scenarios,
            },
            "hostile": hostile_scenarios,  # Now contains both original and CSV scenarios
            "neutral": {
                **neutral_scenarios,
                **neutral_csv_scenarios.neutral_csv_scenarios,
            },
            "high_probability": high_probability_scenarios.high_probability_scenarios,
        }

    def get_scenarios(self, mode: str) -> Dict[str, Any]:
        """Get scenarios for a specific interaction mode.

        Args:
            mode: The interaction mode (friendly, hostile, neutral, high_probability)

        Returns:
            Dict containing scenarios for the specified mode
        """
        return self.scenarios.get(mode, self.scenarios["neutral"])
