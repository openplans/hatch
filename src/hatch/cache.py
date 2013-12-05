from collections import defaultdict
from django.core import cache as django_cache
from django.utils.timezone import now, timedelta

# A sentinel object to differentiate from None
unspecified = object()

class CacheBuffer (object):
    def __init__(self):
        # When we get a value from the remote cache, it goes in to the buffer
        # so that we can retrieve it quickly on our next try.
        self.buffer = {}
        self.timeouts = {}

        # When we set a value, it goes into the queue as well as the buffer.
        # Values are not set in the remote cache from the queue until we call
        # flush.
        self.queue = {}
        self.delete_queue = set()

    def get_many(self, keys):
        results = {}
        unseen_keys = []

        for key in keys:
            try:
                results[key] = self.buffer[key]
            except KeyError:
                unseen_keys.append(key)

        if unseen_keys:
            new_results = django_cache.cache.get_many(unseen_keys)
            if new_results:
                results.update(new_results)
                self.buffer.update(new_results)

        # TODO: Is this what's supposed to happen? get_many returns None for
        #       each key that wasn't found?
        self.buffer.update({key: None for key in set(keys) - set(results.keys())})
        return results

    def get(self, key):
        try:
            return self.buffer[key]
        except KeyError:
            value = django_cache.cache.get(key)
            self.buffer[key] = value
            return value

    def set(self, key, value, timeout=unspecified):
        self.buffer[key] = self.queue[key] = value
        self.timeouts[key] = timeout

        try: self.delete_queue.remove(key)
        except KeyError: pass

    def set_many(self, mapping, timeout=unspecified):
        self.buffer.update(mapping)
        self.queue.update(mapping)

        for key in mapping:
            self.timeouts[key] = timeout

            try: self.delete_queue.remove(key)
            except KeyError: pass

    def delete(self, key):
        try: del self.queue[key]
        except KeyError: pass

        try: del self.buffer[key]
        except KeyError: pass

        try: del self.timeouts[key]
        except KeyError: pass

        self.delete_queue.add(key)

    def delete_many(self, keys):
        for key in keys:
            try: del self.queue[key]
            except KeyError: pass

            try: del self.buffer[key]
            except KeyError: pass

            try: del self.timeouts[key]
            except KeyError: pass

        self.delete_queue.add(keys)

    def flush(self):
        timed_queues = defaultdict(dict)

        if self.queue:
            for key, value in self.queue.iteritems():
                timeout = self.timeouts[key]
                timed_queues[timeout][key] = value

            for timeout, queue in timed_queues.iteritems():
                if timeout is not unspecified:
                    django_cache.cache.set_many(queue, timeout)
                else:
                    django_cache.cache.set_many(queue)

        if self.delete_queue:
            django_cache.cache.delete_many(self.delete_queue)
        
        self.reset()

    def reset(self):
        self.queue = {}
        self.delete_queue = set()
        self.timeouts = {}

cache_buffer = CacheBuffer()
