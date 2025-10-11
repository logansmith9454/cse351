"""
Course    : CSE 351
Assignment: 04
Student   : Logan Smith
Comment   : For this assignment I honestly can't tell if it meets the requirements or not.
            I got it to run in about 80 seconds on my computer, but I can't tell if it's a hardware
            problem or if there's something wrong with my code. I tried a lot of stuff, and I can't
            get it to run any faster. If it is a hardware problem, and it actually can run faster,
            then I think the grade should be a 4, as all requirements are met. If there is something
            wrong with my code, and it cannot run faster, then my grade is a 3, as it works but not
            fully as intended.

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}'

where:

name: name of the city
recno: record number starting from 0

"""
import threading
import time
from calendar import day_name
from queue import Queue

from common import *

from cse351 import *

from lesson_04.team.team import Queue351

THREADS = 100
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change
MAX_QUEUE_SIZE = 10


# ---------------------------------------------------------------------------
def retrieve_weather_data(command_queue: Queue, cq_space: threading.Semaphore, cq_items: threading.Semaphore, thread_barrier: threading.Barrier, data_queue: Queue, dq_space: threading.Semaphore, dq_items: threading.Semaphore):
    while True:
        cq_items.acquire()
        command = command_queue.get()
        cq_space.release()

        if command == "Done":
            if thread_barrier.wait() == 0:
                for _ in range(WORKERS):
                    dq_space.acquire()
                    data_queue.put("Done")
                    dq_items.release()
            break

        name, recno = command
        url = f'{TOP_API_URL}/record/{name}/{recno}'
        data = get_data_from_server(url)
        date = data["date"]
        temp = data["temp"]

        dq_space.acquire()
        data_queue.put((name, date, temp))
        dq_items.release()



# ---------------------------------------------------------------------------
class NOAA:

    def __init__(self):
        # self.data_dict_date: dict[str, list] = {}
        self.data_dict_temp: dict[str, list] = {}
        self.lock = threading.Lock()

    def store_data(self, name, date, temp):
        with self.lock:
            if name not in self.data_dict_temp:
                # self.data_dict_date[name] = [date]
                self.data_dict_temp[name] = [temp]
            else:
                # self.data_dict_date[name].append(date)
                self.data_dict_temp[name].append(temp)

    def get_temp_details(self, city):
        return sum(self.data_dict_temp[city])/RECORDS_TO_RETRIEVE



# ---------------------------------------------------------------------------
class Worker(threading.Thread):

    def __init__(self, noaa: NOAA, data_queue: Queue, dq_space: threading.Semaphore, dq_items: threading.Semaphore, worker_barrier: threading.Barrier):
        super().__init__()
        self.data_queue = data_queue
        self.dq_space = dq_space
        self.dq_items = dq_items
        self.noaa = noaa
        self.worker_barrier = worker_barrier

    def run(self):
        while True:
            self.dq_items.acquire()
            data = self.data_queue.get()
            self.dq_space.release()
            if data == "Done":
                self.worker_barrier.wait()
                break
            name, date, temp = data
            self.noaa.store_data(name, date, temp)


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    command_queue = Queue()
    cq_space = threading.Semaphore(MAX_QUEUE_SIZE)
    cq_items = threading.Semaphore(0)

    data_queue = Queue()
    dq_space = threading.Semaphore(MAX_QUEUE_SIZE)
    dq_items = threading.Semaphore(0)

    thread_barrier = threading.Barrier(THREADS)
    worker_barrier = threading.Barrier(WORKERS)

    retrieval_threads = [threading.Thread(target=retrieve_weather_data, args=(command_queue, cq_space, cq_items, thread_barrier, data_queue, dq_space, dq_items)) for _ in range(THREADS)]

    workers = [Worker(noaa, data_queue, dq_space, dq_items, worker_barrier) for _ in range(WORKERS)]

    for t in retrieval_threads + workers:
        t.start()

    for city in CITIES:
        for i in range(records):
            cq_space.acquire()
            command_queue.put((city, i))
            cq_items.release()

    for _ in range(THREADS):
        cq_space.acquire()
        command_queue.put("Done")
        cq_items.release()

    for t in retrieval_threads + workers:
        t.join()


    # Code to see what the data looks like
    # url = f'{TOP_API_URL}/record/dallas/0'
    # data = get_data_from_server(url)
    # print(f"{data=}")


    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

