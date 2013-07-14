from itertools import combinations, islice
from random import randint


def uniquify_tweet_ids(queryset):
    """Ensure that the tweet_ids of all items in the queryset are unique"""
    all_different = False
    while not all_different:
        all_different = True
        for referrence, other in combinations(queryset, 2):
            if reference.tweet_id == other.tweet_id:
                all_different = False
                other.tweet_id = str(randint(0, 9999999999999999))
                other.save()


def chunk(iterable, n):
    """Collect data into fixed-length chunks"""
    it = iter(iterable)
    while True:
        item = list(islice(it, n))
        if item: yield item
        else: break
