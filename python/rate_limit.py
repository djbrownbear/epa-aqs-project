"""In-process rate limiting for the Gemini-backed chart callback.

Counters live in memory, so each web worker keeps its own; at this app's traffic
that's enough to stop a script from running up the Gemini bill.
"""

import threading
import time
from collections import deque

DAY_SECONDS = 24 * 60 * 60


class RateLimiter:
    def __init__(self, per_client, window_seconds, daily_limit, clock=time.time):
        self.per_client = per_client
        self.window_seconds = window_seconds
        self.daily_limit = daily_limit
        self.clock = clock
        self._lock = threading.Lock()
        self._client_calls = {}
        self._day = None
        self._day_count = 0

    def check(self, client):
        """Record a call for client. Returns None if allowed, else a message for the user."""
        now = self.clock()
        with self._lock:
            day = int(now // DAY_SECONDS)
            if day != self._day:
                self._day, self._day_count = day, 0
            if self._day_count >= self.daily_limit:
                return "The demo has reached its daily limit for generated charts. Please try again tomorrow."

            calls = self._client_calls.setdefault(client, deque())
            while calls and calls[0] <= now - self.window_seconds:
                calls.popleft()
            if len(calls) >= self.per_client:
                return "Too many requests. Please wait a minute and try again."

            calls.append(now)
            self._day_count += 1
            self._prune(now)
            return None

    def _prune(self, now):
        # Drop clients with no calls left in the window so the dict doesn't grow forever.
        cutoff = now - self.window_seconds
        stale = [c for c, calls in self._client_calls.items() if not calls or calls[-1] <= cutoff]
        for c in stale:
            del self._client_calls[c]
