import asyncio
import random
import threading

class TrackQueue(asyncio.Queue):

    def __init__(self):
        super().__init__()
        self.r_lock = threading.Lock()

    def __getitem__(self, item):
        with self.r_lock:
            if isinstance(item, slice):
                return list(itertools.islice(self._queue, item.start, item.stop, item.step))
            else:
                return self._queue[item]

    def __iter__(self):
        with self.r_lock:
            return self._queue.__iter__()

    def __len__(self):
        with self.r_lock:
            return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        with self.r_lock:
            random.shuffle(self._queue)

    def remove(self, idx: int):
        with self.r_lock:
            del self._queue[idx]
