"""
Combines all scenario types into a single SCENARIOS dictionary.
"""

from .friendly_scenarios import friendly_scenarios
from .hostile_scenarios import hostile_scenarios
from .neutral_scenarios import neutral_scenarios
from .chatbot_scenarios import chatbot_scenarios
from .csv_scenarios.neutral_scenarios import neutral_csv_scenarios
from .csv_scenarios.friendly_scenarios import friendly_csv_scenarios
from .csv_scenarios.high_probability_scenarios import high_probability_scenarios

SCENARIOS = {
    "friendly": {**friendly_scenarios, **friendly_csv_scenarios},
    "hostile": hostile_scenarios,  # Now contains both original and CSV scenarios
    "neutral": {**neutral_scenarios, **neutral_csv_scenarios},
    "high_probability": high_probability_scenarios,
    "chatbot": chatbot_scenarios,
}
