from itertools import islice


def chunk(iterable, n):
    "Collect data into fixed-length chunks"
    it = iter(iterable)
    while True:
        item = list(islice(it, n))
        if item: yield item
        else: break
