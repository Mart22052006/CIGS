import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(order=True)
class TweetTask:
    priority: int
    timestamp: float
    gif_filename: Optional[str] = field(compare=False, default=None)
    text: Optional[str] = field(compare=False, default=None)
    reply_to_id: Optional[int] = field(compare=False, default=None)
    attempts: int = field(default=0)


class PriorityTweetQueue:
    PRIORITY_ORDER = {
        "RANDOM_GIFS": 1,
        "RANDOM_POSTS": 2,
        "FRIENDLY": 3,
        "HOSTILE": 4,
        "NEUTRAL": 5,
    }

    @staticmethod
    def get_priority_to_task_type(priority: int) -> str:
        for task_type, task_priority in PriorityTweetQueue.PRIORITY_ORDER.items():
            if task_priority == priority:
                return task_type
        return "UNKNOWN"

    def __init__(self, maxsize: int = 10):
        """
        Initialize the priority-preemptive queue with a maximum size.
        """
        self.queue = asyncio.PriorityQueue(maxsize)

    async def add_task(
        self,
        task_type: str,
        gif_filename: Optional[str] = None,
        text: Optional[str] = None,
        reply_to_id: Optional[int] = None,
        attempts: int = 0,
    ):
        """Add a new task to the queue, preempting a lower priority task if full."""
        priority = self.PRIORITY_ORDER.get(task_type, float("inf"))
        timestamp = time.time()
        new_task = TweetTask(
            priority, timestamp, gif_filename, text, reply_to_id, attempts
        )

        if self.queue.full():
            # Drain the queue
            tasks = []
            while not self.empty():
                t = await self.queue.get()
                # We immediately call task_done() for these because we're temporarily removing them
                # for re-prioritization and will re-add them. This ensures the queue's internal counter
                # remains consistent.
                self.queue.task_done()
                tasks.append(t)

            # Add our new task to the list
            tasks.append(new_task)

            # Sort tasks by priority and timestamp
            tasks.sort(key=lambda t: (t.priority, t.timestamp))

            # Drop the lowest-priority (last) task
            dropped_task = tasks.pop()

            # Now put back all the tasks except the dropped one
            for t in tasks:
                await self.queue.put(t)

            logger.info(f"Queue full! Removed lower-priority task: {dropped_task}")
            logger.info(f"Added high-priority task: {new_task}")
        else:
            await self.queue.put(new_task)
            logger.info(f"Task added: {new_task}")

    def view_queue(self) -> list:
        return list(self.queue._queue)

    async def get_task(self):
        """Retrieve the next task."""
        return await self.queue.get()

    def task_done(self):
        """Mark a task as done."""
        self.queue.task_done()

    async def join(self):
        """Wait until all tasks are processed."""
        await self.queue.join()

    def empty(self):
        """Check if the queue is empty."""
        return self.queue.empty()
