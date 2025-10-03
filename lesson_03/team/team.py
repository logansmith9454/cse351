"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.  The function should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
from queue import Queue

from common import *

# Include cse 351 common Python files
from cse351 import *


# global
call_count = 0

class CallServer(threading.Thread):
    def __init__(self, url, data):
        super().__init__()
        self.kind = url[0]
        self.url = url[1]
        self.data = data
        self.local_count = 0

    def run(self):
        item = get_data_from_server(self.url)
        self.data[self.kind].append(item)
        # print(f'  - {item['name']}', flush=True)

# def get_urls(film6, kind):
#     global call_count
#
#     urls = film6[kind]
#     print(kind, flush=True)
#     for url in urls:
#         call_count += 1
#         item = get_data_from_server(url)
#         print(f'  - {item['name']}', flush=True)

def main():
    global call_count
    data = {}

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1

    kinds = ['characters', 'planets', 'starships', 'vehicles', 'species']
    q = Queue()
    for kind in kinds:
        data[kind] = []
        for item in film6[kind]:
            q.put((kind, item))
    q.put(None)

    threads = []
    still_running = True
    while still_running:
        url = q.get()
        if url is None:
            break
        t = CallServer(url, data)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
        call_count += 1

    for kind in data:
        print(kind)
        for item in data[kind]:
            print(f'  - {item['name']}', flush=True)

    # Retrieve people
    # get_urls(film6, 'characters')
    # get_urls(film6, 'planets')
    # get_urls(film6, 'starships')
    # get_urls(film6, 'vehicles')
    # get_urls(film6, 'species')

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()