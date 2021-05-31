
import logging
import random

from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

base = 10
cap = 2*24*3600 # 2 days


def backoff_with_jitter(attempt):
    return random.randrange(min(cap, (base-5) * 2 ** attempt), min(cap, base * 2 ** attempt))

def next_time(cur_time: datetime, attempt: int) -> datetime:
    return cur_time + timedelta(seconds = backoff_with_jitter(attempt))

