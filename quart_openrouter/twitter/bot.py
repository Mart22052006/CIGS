import asyncio
import json
import logging
import os
import random
import re
import time
import uuid
import io
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse, unquote

import dotenv
# import tweepy
from httpx import get

# ============ Import your data from agent1_data.py ============
# This file holds your random texts, gifs, and tags
from quart_openrouter.data.agent1_data import (
    RANDOM_TEXTS,
    RANDOM_GIFS,
    RANDOM_TAGS,
    FRIENDLY_X_ID_TO_HANDLE,
    HOSTILE_X_ID_TO_HANDLE,
)

from quart_openrouter.openrouter_client import OpenRouterClient
# from quart_openrouter.twitter.priority_queue import PriorityTweetQueue
from quart_openrouter.ai_client import AIClient
from quart_openrouter.personality import Agent1Personality, TwitterPersonality

# Resolve and normalize the .env path
env_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

# Debugging
print(f"Loading .env file from: {env_path}")

# Check if .env exists
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at: {env_path}")

# Load .env
dotenv.load_dotenv(env_path)
# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Version 1.2 with rate limit of 4 tweets/user/hr is now running...")
'''
def get_api() -> tweepy.API:
    """
    Get an authenticated Tweepy API instance for media uploads.
    """
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key=os.getenv("X_CONSUMER_KEY"),
            consumer_secret=os.getenv("X_CONSUMER_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        )
        return tweepy.API(auth)
    except Exception as e:
        logging.error(f"Error creating API instance: {e}")
        exit(1)


def get_client() -> tweepy.Client:
    """
    Authenticate and return a Tweepy client instance.
    """
    try:
        client = tweepy.Client(
            bearer_token=os.getenv("X_BEARER_TOKEN"),
            consumer_key=os.getenv("X_CONSUMER_KEY"),
            consumer_secret=os.getenv("X_CONSUMER_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        )
        return client
    except Exception as e:
        logging.error(f"Error while authenticating: {e}")
        exit(1)

'''
class Bot:
    def __init__(
        self,
        personality: TwitterPersonality,
        ai_client: AIClient,
        # twitter_client: tweepy.Client,
        # twitter_api: tweepy.API,
        bot_id: int,
    ):
        self.personality = personality
        self.ai_client = ai_client
        # self.client = twitter_client
        # self.api = twitter_api
        self.BOT_ID = bot_id

        # Initialize Priority Tweet Queue
        self.priority_queue = PriorityTweetQueue(maxsize=100)

        # Time management
        self.last_interaction = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        self.last_random_post_time = None  # Track only random posts
        self.random_post_interval = timedelta(hours=4)

        # ========= Non-repeating random text tweets =========
        self.proactive_tweets = list(RANDOM_TEXTS)
        random.shuffle(self.proactive_tweets)
        self.proactive_index = 0

        # Mention tracking for rate limiting
        # Key: user_id, Value: list of datetimes of mentions (within the last hour)
        self.mention_tracker = {}

    def view_queue(self) -> list:
        """For debugging: see what's currently in the queue."""
        return self.priority_queue.view_queue()

    def get_random_friendly_handle(self) -> str:
        """Uses the personality's logic to pick a friendly handle"""
        return self.personality.get_random_friendly_handle()

    def is_friendly_user(self, user_id: int) -> bool:
        """Check if user is in the friendly list."""
        return self.personality.is_friendly_user(user_id)

    def is_hostile_user(self, user_id: int) -> bool:
        """Check if user is in the hostile list."""
        return self.personality.is_hostile_user(user_id)

    def get_next_proactive_tweet(self) -> str:
        """
        Return the next text from the shuffled `RANDOM_TEXTS`.
        When all texts are used, reshuffle and start over.
        """
        if self.proactive_index >= len(self.proactive_tweets):
            random.shuffle(self.proactive_tweets)
            self.proactive_index = 0

        text = self.proactive_tweets[self.proactive_index]
        self.proactive_index += 1
        return text

    def make_post(self, tweet: Optional[str], gif_filename: Optional[str], is_random: bool = False):
        """
        Post either a tweet or a GIF (not both) to the authenticated user's timeline.
        """
        logging.info(f"Tweet: {tweet}")
        logging.info(f"GIF: {gif_filename}")
        try:
            if not tweet and not gif_filename:
                logging.info("No tweet text or GIF found to post.")
                return

            if gif_filename:
                media_id = self.upload_media(gif_filename)
                if media_id:
                    self.client.create_tweet(text=tweet, media_ids=[media_id])
                    logging.info("Posted successfully with GIF!")
                else:
                    logging.error(f"Failed to upload GIF {gif_filename}")
                    fallback_text = self.personality.get_random_text()
                    self.client.create_tweet(text=fallback_text)
            else:
                self.client.create_tweet(text=tweet)
                logging.info("Posted successfully without GIF!")

            # Update last random post time only for random posts
            if is_random:
                self.last_random_post_time = datetime.now()
                logging.info(f"Updated last random post time to {self.last_random_post_time}")

        except Exception as e:
            logging.error(f"Error while posting: {e}")
            raise e

    def reply_to_mention(
        self,
        tweet: str,
        reply_to_tweet_id: int,
        gif_filename: Optional[str],
    ):
        """
        Reply to a tweet with optional GIF.
        """
        logging.info(f"Replying to tweet ID: {reply_to_tweet_id}")
        logging.info(f"Tweet: {tweet}")
        logging.info(f"GIF: {gif_filename}")
        try:
            if not tweet and not gif_filename:
                logging.info("No tweet text or GIF found to reply with.")
                return

            if gif_filename:
                media_id = self.upload_media(gif_filename)
                if media_id:
                    self.client.create_tweet(
                        text=tweet,
                        in_reply_to_tweet_id=reply_to_tweet_id,
                        media_ids=[media_id],
                    )
                    logging.info("Replied successfully with GIF!")
                else:
                    logging.error(f"Failed to upload GIF {gif_filename}")
                    self.client.create_tweet(
                        text=tweet, in_reply_to_tweet_id=reply_to_tweet_id
                    )
            else:
                self.client.create_tweet(
                    text=tweet, in_reply_to_tweet_id=reply_to_tweet_id
                )
                logging.info("Replied successfully without GIF!")

        except Exception as e:
            logging.error(f"Error while replying: {e}")
            raise e

    def upload_media(self, gif_filename: str) -> Optional[int]:
        """
        Upload a GIF (or any media file) and return its media ID.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            quart_dir = os.path.dirname(current_dir)  # Go up one level
            gif_path = os.path.join(quart_dir, "static", "gifs", "based", gif_filename)
            logging.info(f"Attempting to load GIF from: {gif_path}")

            with open(gif_path, "rb") as f:
                gif_data = f.read()
                media = self.api.media_upload(
                    filename=gif_filename,
                    file=io.BytesIO(gif_data)
                )
                return media.media_id

        except Exception as e:
            logging.error(f"Error uploading GIF {gif_filename}: {e}")
            return None

    async def add_random_posts(self):
        """
        Add a random post to the priority queue every 2 hours.
        """
        # Sleep 2 hours before first random post
        await asyncio.sleep(7200)

        while True:
            rand_val = random.random()
            # 20% => GIF-only
            if rand_val < 0.2:
                gif_filename = random.choice(RANDOM_GIFS)
                text = None
                task_type = "RANDOM_GIFS"
            # Next 40% => text-only
            elif rand_val < 0.6:
                gif_filename = None
                text = self.get_next_proactive_tweet()
                task_type = "RANDOM_POSTS"
            # Last 40% => text + friendly mention
            else:
                gif_filename = None
                text = f"{self.get_random_friendly_handle()} {self.get_next_proactive_tweet()}"
                task_type = "RANDOM_POSTS"

            await self.priority_queue.add_task(
                task_type=task_type,
                text=text,
                reply_to_id=None,
                gif_filename=gif_filename,
            )

            logging.info("Added a random post to the queue.")
            await asyncio.sleep(7200)  # Sleep 2 hours

    async def should_process_task(self, task_type: str) -> bool:
        """
        Determine if we should process a task based on the last post time
        and the task type. Only rate limits random posts.
        """
        # If it's a reply to a mention, always allow it
        if task_type in ["FRIENDLY", "HOSTILE", "NEUTRAL"]:
            return True

        # For random posts, enforce the interval
        if task_type in ["RANDOM_GIFS", "RANDOM_POSTS"]:
            if not self.last_random_post_time:
                return True

            time_since_last_post = datetime.now() - self.last_random_post_time
            return time_since_last_post >= self.random_post_interval

        return True  # Default allow for any other task types

    async def get_mentions(self, test_mode=False):
        """
        Periodically checks for new mentions in smaller batches (max_results=20)
        and aggregates them. Includes rate limiting via mention_tracker 
        and handles 429 with x-rate-limit-reset logic.
        """
        while True:
            logging.info("Checking for new mentions in batches of 20.")

            try:
                # We'll fetch 1 page of results (1 x 20 = 20 mentions max).
                # Adjust 'max_pages' to control how many times you paginate per cycle.
                max_pages = 1
                page_count = 0
                pagination_token = None
                all_mentions = []

                while page_count < max_pages:
                    mentions_response = self.client.get_users_mentions(
                        id=self.BOT_ID,
                        start_time=self.last_interaction,
                        max_results=20,  # <--- smaller batch size
                        expansions=["author_id"],
                        pagination_token=pagination_token,
                    )

                    # If we got data back, extend our list of new mentions
                    if mentions_response.data:
                        all_mentions.extend(mentions_response.data)

                    # If there's no 'next_token', we're done paginating
                    if (not mentions_response.meta) or ("next_token" not in mentions_response.meta):
                        break

                    # Otherwise, update pagination_token to fetch the next batch
                    pagination_token = mentions_response.meta["next_token"]
                    page_count += 1

                # Update the 'last_interaction' to the current time, 
                # so next fetch only gets newer mentions.
                self.last_interaction = datetime.utcnow().isoformat(timespec="seconds") + "Z"

            except tweepy.TooManyRequests as e:
                logging.error("Rate limit exceeded while fetching mentions.")
                # Attempt to parse the x-rate-limit-reset header
                reset_time = e.response.headers.get('x-rate-limit-reset')
                if reset_time:
                    sleep_secs = int(reset_time) - int(time.time())
                    if sleep_secs > 0:
                        logging.info(f"Rate limit hit, sleeping for {sleep_secs} seconds...")
                        await asyncio.sleep(sleep_secs)
                else:
                    logging.info("Rate limit hit, sleeping for 15 minutes (no reset header found).")
                    await asyncio.sleep(900)
                continue

            except Exception as e:
                logging.error(f"Error while fetching mentions: {e}")
                # Sleep ~15 minutes if unexpected error
                await asyncio.sleep(905)
                continue

            if not all_mentions:
                logging.info("No new mentions found.")
            else:
                logging.info(f"Found {len(all_mentions)} new mentions.")
                for mention in all_mentions:
                    # Skip if the bot is the author (avoid responding to self)
                    if mention.author_id == self.BOT_ID:
                        continue

                    # Rate-limiting logic by mention count
                    now = datetime.now()
                    one_hour_ago = now - timedelta(hours=1)

                    # Initialize if not tracked
                    if mention.author_id not in self.mention_tracker:
                        self.mention_tracker[mention.author_id] = []

                    # Remove mentions older than 1 hour
                    self.mention_tracker[mention.author_id] = [
                        t for t in self.mention_tracker[mention.author_id] if t > one_hour_ago
                    ]

                    # Check how many mentions are in the last hour
                    if len(self.mention_tracker[mention.author_id]) >= 4:
                        logging.info(
                            f"Skipping mention from user {mention.author_id} due to rate limiting."
                        )
                        continue

                    # Add current mention timestamp
                    self.mention_tracker[mention.author_id].append(now)

                    gif_filename = None
                    ai_response = None

                    if self.is_friendly_user(mention.author_id):
                        task_type = "FRIENDLY"
                        mode = "friendly"
                    elif self.is_hostile_user(mention.author_id):
                        task_type = "HOSTILE"
                        mode = "hostile"
                    else:
                        task_type = "NEUTRAL"
                        mode = "neutral"

                    rand_val = random.random()
                    if rand_val < 0.05:
                        ai_response = random.choice(RANDOM_TEXTS)
                    elif rand_val < 0.0763158:
                        gif_filename = random.choice(RANDOM_GIFS)
                        ai_response = None
                    else:
                        try:
                            ai_response = await self.ai_client.generate_response(
                                mention.text, mode, self.personality
                            )
                        except Exception as ex:
                            logging.error(f"Error while generating response: {ex}")
                            ai_response = random.choice(RANDOM_TEXTS)

                    # Finally, add the task to the priority queue
                    await self.priority_queue.add_task(
                        task_type=task_type,
                        text=ai_response,
                        reply_to_id=mention.id,
                        gif_filename=gif_filename,
                    )

            if test_mode:
                break

            # Sleep 3 minutes between checks (adjust as needed)
            await asyncio.sleep(180)

    async def consume_queue(self, test_mode=False):
        """
        Process tasks from the priority queue with rate limiting for random posts only.
        """
        await asyncio.sleep(5)

        while True:
            if self.priority_queue.empty():
                if test_mode:
                    break
                await asyncio.sleep(60)
                continue

            task = await self.priority_queue.get_task()
            task_type = self.priority_queue.get_priority_to_task_type(task.priority)

            # Check if we should process this task based on rate limiting
            if not await self.should_process_task(task_type):
                # Put the task back in the queue and wait
                await self.priority_queue.add_task(
                    task_type=task_type,
                    text=task.text,
                    reply_to_id=task.reply_to_id,
                    gif_filename=task.gif_filename,
                )
                await asyncio.sleep(60)
                continue

            try:
                if task_type in ["RANDOM_GIFS", "RANDOM_POSTS"]:
                    self.make_post(
                        tweet=task.text,
                        gif_filename=task.gif_filename,
                        is_random=True  # Mark as random post for timing tracking
                    )
                else:
                    self.reply_to_mention(
                        tweet=task.text,
                        reply_to_tweet_id=task.reply_to_id,
                        gif_filename=task.gif_filename,
                    )
            except tweepy.Forbidden as e:
                # Duplicate tweet error or user-initiated block
                if e.api_codes and 187 in e.api_codes:
                    logging.error("Duplicate tweet detected. Skipping post.")
                    # Try a new random text instead
                    task.text = random.choice(RANDOM_TEXTS)
                    await self.priority_queue.add_task(
                        task_type=task_type,
                        text=task.text,
                        reply_to_id=task.reply_to_id,
                        gif_filename=task.gif_filename,
                    )
                else:
                    self.handle_posting_error(e, task_type, task)
            except tweepy.TooManyRequests as e:
                logging.error("Rate limit exceeded while posting.")
                # Attempt to parse the x-rate-limit-reset header
                reset_time = e.response.headers.get('x-rate-limit-reset')
                if reset_time:
                    sleep_secs = int(reset_time) - int(time.time())
                    if sleep_secs > 0:
                        logging.info(f"Rate limit hit, sleeping for {sleep_secs} seconds...")
                        await asyncio.sleep(sleep_secs)
                else:
                    logging.info("Rate limit hit, sleeping for 15 minutes (no reset header found).")
                    await asyncio.sleep(900)
                continue
            except Exception as e:
                self.handle_posting_error(e, task_type, task)

            self.priority_queue.task_done()

    def handle_posting_error(self, e: Exception, task_type: str, task):
        """
        Generic error handler when posting fails.
        We attempt to re-queue once. After that, we skip the post.
        """
        logging.error(f"Error while posting: {e}")
        task.attempts += 1
        if task.attempts < 2:
            asyncio.run(
                self.priority_queue.add_task(
                    task_type=task_type,
                    text=task.text,
                    reply_to_id=task.reply_to_id,
                    gif_filename=task.gif_filename,
                    attempts=task.attempts,
                )
            )
        else:
            logging.error("Failed to post after 2 attempts. Skipping post.")

    async def run(self):
        """
        Main entry to run the bot. Gathers coroutines for:
         1) Checking mentions and queueing replies
         2) Adding random posts to the queue
         3) Consuming (posting) from the queue
        """
        if not self.BOT_ID:
            logging.error("Failed to get authenticated user ID.")
            exit(1)

        if os.getenv("ENV", "dev") == "prod":
            # Production mode
            await asyncio.gather(
                self.get_mentions(),
                self.add_random_posts(),
                self.consume_queue(),
            )
        else:
            # Test mode
            logging.info("Running in test mode. Sleeping for 10 minutes...")
            # Add a dummy task to queue for demonstration
            await self.priority_queue.add_task(
                task_type="RANDOM_POSTS",
                text="Test tweet",
                reply_to_id=None,
                gif_filename=None,
            )

            await asyncio.sleep(600)
            logging.info("Shutting down.")


if __name__ == "__main__":
    personality = Agent1Personality("BASED", ["crypto", "trading"])
    lm_client = OpenRouterClient(os.getenv("OPEN_ROUTER_API_KEY", ""))
    ai_client = AIClient(lm_client)
    # twitter_client = get_client()
    # twitter_api = get_api()
    # bot_id = twitter_client.get_me().data.id

    if not bot_id:
        logging.error("Failed to get authenticated user ID.")
        exit(1)

    bot = Bot(personality, ai_client, twitter_client, twitter_api, bot_id)
    asyncio.run(bot.run())
