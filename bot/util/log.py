import logging
import asyncio

import logging.config
import logging.handlers
from queue import SimpleQueue as Queue

logging.config.fileConfig(fname='logging.conf')

class LocalQueueHandler(logging.handlers.QueueHandler):
    def emit(self, record) -> None:
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)

def setup_logging_queue() -> None:
    queue = Queue()
    root = logging.getLogger()

    handlers: List[logging.Handler] = []

    handler = LocalQueueHandler(queue)
    root.addHandler(handler)
    for h in root.handlers[:]:
        if h is not handler:
            root.removeHandler(h)
            handlers.append(h)
    listener = logging.handlers.QueueListener(queue, *handlers, respect_handler_level=True)
    listener.start()
