from django.test import TestCase
from django.core.cache import cache
from ..cache import CacheBuffer
from mock import patch, Mock


class CacheBufferTest (TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_flushing_sets_queued_values(self):
        b = CacheBuffer()
        b.set('key1', 'val1')
        b.set('key2', 'val2')

        self.assertEqual(b.queue, {'key1': 'val1', 'key2': 'val2'})
        self.assertEqual(cache.get_many(['key1', 'key2']), {})

        b.flush()

        self.assertEqual(cache.get_many(['key1', 'key2']), {'key1': 'val1', 'key2': 'val2'})

    def test_flushing_deletes_queued_values(self):
        values = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
        cache.set_many(values)
        b = CacheBuffer(values)

        b.delete('a')
        b.delete('b')

        self.assertEqual(b.delete_queue, set(['a', 'b']))
        self.assertEqual(cache.get_many(['a', 'b']), {'a': 1, 'b': 2})

        b.flush()

        self.assertEqual(cache.get_many(['a', 'b']), {})

    def test_set_many_adds_keys_to_queue(self):
        b = CacheBuffer({'a': 1, 'b': 2})
        
        b.set_many({'b': 6, 'c': 7})
        b.set_many({'c': 3, 'd': 4})
        self.assertEqual(b.queue, {'b': 6, 'c': 3, 'd': 4})

    def test_delete_adds_keys_to_delete_queue(self):
        b = CacheBuffer({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})
        
        b.delete('a')
        b.delete('b')
        self.assertEqual(b.delete_queue, set(['a', 'b']))

    def test_delete_many_adds_keys_to_delete_queue(self):
        b = CacheBuffer({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})
        
        b.delete_many(['a', 'b'])
        b.delete_many(['b', 'd'])
        self.assertEqual(b.delete_queue, set(['a', 'b', 'd']))
