from rate_limit import DAY_SECONDS, RateLimiter


class FakeClock:
    def __init__(self, now=1_000_000.0):
        self.now = now

    def __call__(self):
        return self.now


def make_limiter(clock, per_client=2, daily_limit=5):
    return RateLimiter(per_client=per_client, window_seconds=60, daily_limit=daily_limit, clock=clock)


def test_blocks_a_client_over_the_per_minute_limit():
    limiter = make_limiter(FakeClock())

    assert limiter.check("a") is None
    assert limiter.check("a") is None
    assert "Too many requests" in limiter.check("a")
    assert limiter.check("b") is None


def test_client_is_allowed_again_after_the_window():
    clock = FakeClock()
    limiter = make_limiter(clock)
    limiter.check("a")
    limiter.check("a")

    clock.now += 60

    assert limiter.check("a") is None


def test_daily_limit_applies_across_clients_and_resets_next_day():
    clock = FakeClock(now=3 * DAY_SECONDS)
    limiter = make_limiter(clock, per_client=10, daily_limit=3)
    for client in ("a", "b", "c"):
        assert limiter.check(client) is None

    assert "daily limit" in limiter.check("d")

    clock.now += DAY_SECONDS
    assert limiter.check("d") is None


def test_blocked_calls_do_not_count():
    clock = FakeClock()
    limiter = make_limiter(clock, per_client=1, daily_limit=2)
    limiter.check("a")
    limiter.check("a")  # blocked

    assert limiter.check("b") is None


def test_idle_clients_are_pruned():
    clock = FakeClock()
    limiter = make_limiter(clock)
    limiter.check("a")

    clock.now += 61
    limiter.check("b")

    assert set(limiter._client_calls) == {"b"}
