"""
Course: CSE 351
Lesson: L01 Team Activity
File:   team.py
Author: <Add name here>
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)

TODO 1) Get this program running.  Get cse351 package installed
TODO 2) move the following for loop into 1 thread
TODO 3) change the program to divide the for loop into 10 threads
TODO 4) change range_count to 100007.  Does your program still work?  Can you fix it?
Question: if the number of threads and range_count was random, would your program work?
"""

from datetime import datetime, timedelta
import threading
import random

# Include cse 351 common Python files
from cse351 import *

# Global variable for counting the number of primes found
prime_count = 0
numbers_processed = 0

def is_prime(n):
    """
        Primality test using 6k+-1 optimization.
        From: https://en.wikipedia.org/wiki/Primality_test
    """
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

class PrimeChecker(threading.Thread):
    def __init__(self, range_count: int, start: int, num_processed_lock: threading.Lock, prime_count_lock: threading.Lock):
        super().__init__()
        self.start_value = start
        self.range_count = range_count
        self.prime_count_lock = prime_count_lock
        self.num_processed_lock = num_processed_lock
        self.num_processed = 0
        self.prime_count = 0

    def run(self):
        # process_primes(self.range_count, self.start_value, self.num_processed_lock, self.prime_count_lock)
        # global numbers_processed, prime_count
        # local_numbers_processed = 0
        # local_prime_count = 0
        for i in range(self.start_value, self.start_value + self.range_count):
            self.num_processed += 1
            if is_prime(i):
                self.prime_count += 1
                print(i, end=', ', flush=True)

        # with self.num_processed_lock:
        #     numbers_processed += local_numbers_processed
        #
        # self.prime_count_lock.acquire()
        # prime_count += local_prime_count
        # self.prime_count_lock.release()
        # update result



def main():
    # global prime_count                  # Required in order to use a global variable
    # global numbers_processed            # Required in order to use a global variable

    log = Log(show_terminal=True)
    log.start_timer()

    start = 10_000_000_000
    range_count = 100_000
    # numbers_processed = 0
    threads = []
    num_processed_lock = threading.Lock()
    prime_count_lock = threading.Lock()
    for i in range(100):
        # t = threading.Thread(target=process_primes, args=(range_count // 100, start + (range_count // 100 * i), num_processed_lock, prime_count_lock))
        t = PrimeChecker(range_count // 100, start + (range_count // 100 * i), num_processed_lock, prime_count_lock)
        # process_primes(range_count, start)
        t.start()
        threads.append(t)

    local_numbers_processed = 0
    local_prime_count = 0
    for t in threads:
        t.join()
        local_numbers_processed += t.num_processed
        local_prime_count += t.prime_count
    print(flush=True)

    # Should find 4306 primes
    log.write(f'Numbers processed = {local_numbers_processed}')
    log.write(f'Primes found      = {local_prime_count}')
    log.stop_timer('Total time')


def process_primes(range_count: int, start: int, num_processed_lock: threading.Lock, prime_count_lock: threading.Lock):
    global numbers_processed, prime_count
    local_numbers_processed = 0
    local_prime_count = 0
    for i in range(start, start + range_count):
        local_numbers_processed += 1
        if is_prime(i):
            local_prime_count += 1
            print(i, end=', ', flush=True)

    with num_processed_lock:
        numbers_processed += local_numbers_processed

    prime_count_lock.acquire()
    prime_count += local_prime_count
    prime_count_lock.release()

if __name__ == '__main__':
    main()