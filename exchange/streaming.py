import queue
from queue import Queue
from abc import ABC, abstractmethod


class Service(ABC):
    """
    Interface for streaming video and audio services

    Protected:
        _exception_queue : Queue
            queue for the exception storage
        _running: bool
            parameter that represents if the process runs

    """
    def __init__(self):
        self._exception_queue: Queue = Queue()
        self._running: bool = False

    @abstractmethod
    def start_service(self):
        pass

    @abstractmethod
    def stop_service(self):
        pass

    def get_exceptions(self) -> Queue:
        return self._exception_queue

    def has_exceptions(self) -> bool:
        return not self._exception_queue.empty()

    def _add_exception_to_queue(self, exception: Exception):
        if self._running:
            self._running = False
            self._exception_queue.put(exception)
