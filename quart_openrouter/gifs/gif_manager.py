from typing import Dict, List, Optional
from dotenv import load_dotenv
import random
import logging
import os

load_dotenv()

URL = os.getenv("GIF_URL", "http://localhost:5000") + "/conversation/gifs/based/"

logger = logging.getLogger(__name__)


class GifManager:
    """Manages GIF selection and probability-based serving for different scenarios."""

    def __init__(self):
        """Initialize GifManager with predefined GIF mappings."""
        self.gif_mappings: Dict[str, List[str]] = {
            "anybody_who_tries_to_control_the_conversation": ["comb.gif"],
            "new_neutral_interacts": ["hey1.gif", "hey2.gif", "hey3.gif", "cells.gif"],
            "mentions_mom_or_dad": ["cry.gif", "guard.gif"],
            "mentions_soap": ["shower.gif"],
            "general_convo": ["pull_up.gif", "cells.gif"],
            "asked_about_leaving_jail": ["guard.gif", "marching.gif"],
            "asking_technical_questions_about_mindpalace": ["lipstick1.gif"],
            "mentions_making_money_or_tokens_increasing_in_value": [
                "guard.gif",
            ],
            "mentions_selling_ai": ["comb.gif"],
            "asking_about_women_in_jail": ["cells.gif", "marching.gif"],
            "mentions_buying_ai_or_supporting_mindpalace": [
                "marching.gif",
            ],
            "mentions_race_or_racism": ["shanking.gif", "threat1.gif"],
            "direct_threat": ["shanking.gif", "shower.gif", "pocket1.gif", "pocket2.gif", "lipstick.gif"],
            # "none_applicable": ["shanking.gif", "shower.gif", "pocket1.gif", "pocket2.gif", "lipstick.gif"],
            "insult_derogatory": ["shanking.gif", "shower.gif", "pocket1.gif", "pocket2.gif", "lipstick.gif"],
            "says_hello": ["hey1.gif", "hey2.gif", "hey3.gif", "hey5.gif"],
            "mentions_the_word_funny_or_funnier": ["hey3.gif", "hey5.gif"],
            "asks_about_techincal_code": ["lipstick1.gif"],
        }

        self.gif_mapping_meanings = {
            "cells.gif": "Sup homie. You seem nervous. Come over here",
            "comb.gif": "Good boy. Yes",
            "cry.gif": "I was hoping for nudz Maybe next time",
            "guard.gif": "Come on guard…. Me and the boys were about to turn that vegan into a meat wagon",
            "hey1.gif": "Good morning my little jeets. Everyone hit the showers in 15",
            "hey2.gif": "Gm inmate #69420",
            "hey3.gif": "Sup fresh bootyholes",
            "hey4.gif": "Who ready to come visit me",
            "hey5.gif": "Fresh air is good today",
            "hey6.jpg": "Who ready to come visit me",  # This is a JPG, not a GIF
            "lipstick1.gif": "Here… put this on those soft lips",
            "marching.gif": "Sup guards. Let ya boi have some fun",
            "pocket1.gif": "Very tight sphincter",
            "pocket2.gif": "Never Need bootyhole pics",
            "pull up.gif": "Kinda horny",
            "shanking.gif": "Can i stab???",
            "shower.gif": "Change don’t to please",
            "threat1.gif": "He ded. Sorry… not sorry",
        }

        # Default probability for returning a GIF
        self.default_probability = 0.3

    def get_gif_for_scenario(
        self, scenario: str, probability: Optional[float] = None
    ) -> Optional[str]:
        """Get a GIF URL for a given scenario with probability.

        Args:
            scenario (str): The scenario name
            probability (Optional[float], optional): Probability of returning a GIF.
                Defaults to self.default_probability.

        Returns:
            Optional[str]: GIF URL or None if no GIF should be returned
        """
        try:
            prob = probability if probability is not None else self.default_probability

            # Check probability first
            if random.random() > prob:
                return None

            # Get GIFs for scenario
            gifs = self.gif_mappings.get(scenario, [])
            if not gifs:
                logger.debug(f"No GIFs found for scenario: {scenario}")
                return None

            # Return random GIF
            selected_gif = random.choice(gifs)
            logger.debug(f"Selected GIF {selected_gif} for scenario {scenario}")
            return URL + selected_gif

        except Exception as e:
            logger.error(f"Error getting GIF for scenario '{scenario}': {str(e)}")
            return None

    def get_random_gif(self, gifs: Optional[List[str]] = None) -> Optional[str]:
        """Get a random GIF from a list with probability.

        Args:
            probability (float, optional): Probability of returning a GIF.
                Defaults to self.default_probability.
            gifs (Optional[List[str]], optional): List of GIFs to choose from.
                Defaults to None.

        Returns:
            Optional[str]: GIF URL or None if no GIF should be returned
        """
        try:
            # prob = probability if probability is not None else self.default_probability

            # # Check probability first
            # if random.random() > prob:
            #     return None

            # If no GIFs provided, use default list
            gif_list = gifs if gifs else ["hey1.gif", "hey2.gif", "hey3.gif"]
            gif = random.choice(gif_list)
            return URL + gif

        except Exception as e:
            logger.error(f"Error getting random GIF: {str(e)}")
            return None

    def get_gif_meaning(self, gif_path: str) -> str:
        """Get the meaning of a GIF.

        Args:
            gif_path (str): The path to the GIF

        Returns:
            str: The meaning of the GIF
        """
        gif_name = gif_path.split("/")
        gif_name = gif_name[-1]
        return self.gif_mapping_meanings.get(gif_name, "Good boy. Yes")

    def get_all_gif_urls(self) -> List[str]:
        """Get all GIF URLs.

        Returns:
            List[str]: List of all GIF URLs
        """
        gif_urls = []
        for gif_list in self.gif_mappings.values():
            for gif in gif_list:
                gif_urls.append(URL + gif)
        return gif_urls
