""" 
Course: CSE 351
Team  : Week 04
File  : team.py
Author: Logan Smith

See instructions in canvas for this team activity.

"""

import random
import threading
from typing import Any

# Include CSE 351 common Python files. 
from cse351 import *
from rchitect.console import flush

# Constants
MAX_QUEUE_SIZE = 10
PRIME_COUNT = 1000
FILENAME = 'primes.txt'
PRODUCERS = 3
CONSUMERS = 5

# ---------------------------------------------------------------------------
def is_prime(n: int):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self) -> Any:
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra

# ---------------------------------------------------------------------------
def producer(que: Queue351, space_available: threading.Semaphore, items_available: threading.Semaphore, barrier: threading.Barrier):
    for i in range(PRIME_COUNT):
        number = random.randint(1, 1_000_000_000_000)
        # TODO - place on queue for workers
        space_available.acquire()
        que.put(number)
        items_available.release()

    # TODO - select one producer to send the "All Done" message
    if barrier.wait() == 0:
        for i in range(CONSUMERS):
            space_available.acquire()
            que.put("All Done")
            items_available.release()

# ---------------------------------------------------------------------------
def consumer(que: Queue351, space_available: threading.Semaphore, items_available: threading.Semaphore, filename: str, file_lock: threading.Lock):
    while True:
        items_available.acquire()
        number = que.get()
        space_available.release()
        if number == "All Done":
            break
        elif is_prime(number):
            with file_lock:

                with open(filename, 'a') as f:
                    f.write(f"{number}\n")


    ...

# ---------------------------------------------------------------------------
def main():

    random.seed(102030)
    open(FILENAME, "w").close()

    que = Queue351()

    space_available = threading.BoundedSemaphore(MAX_QUEUE_SIZE)
    items_available = threading.BoundedSemaphore(MAX_QUEUE_SIZE)
    for _ in range(MAX_QUEUE_SIZE):
        items_available.acquire()

    barrier = threading.Barrier(PRODUCERS)

    file_lock = threading.Lock()

    threads = []

    # TODO - create producers threads (see PRODUCERS value)
    producers = [threading.Thread(target=producer, args=(que, space_available, items_available, barrier)) for _ in range(PRODUCERS)]

    # TODO - create consumers threads (see CONSUMERS value)
    consumers = [threading.Thread(target=consumer, args=(que, space_available, items_available, FILENAME, file_lock)) for _ in range(CONSUMERS)]

    for t in producers + consumers:
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            primes = len(f.readlines())
    else:
        primes = 0
    print(f"Found {primes} primes. Must be 108 found.")



if __name__ == '__main__':
    main()
