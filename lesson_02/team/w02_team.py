"""
Course: CSE 351 
Lesson: L02 team activity
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
- Create a threaded class to make a call to the server where
  it retrieves data based on a URL.  The class should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded class should only retrieve one URL.
  
- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading

from common import *

# Include cse 351 common Python files
from cse351 import *

class RequestKind(threading.Thread):
    def __init__(self, film6, kind: str):
        super().__init__()
        self.film6 = film6
        self.kind = kind
        self.local_count = 0
        self.urls = self.film6[self.kind]

    def run(self):
        url_threads = []
        for url in self.urls:
            self.local_count += 1
            t = RequestURL(url)
            t.start()
            url_threads.append(t)

        for t in url_threads:
            t.join()


class RequestURL(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        item = get_data_from_server(self.url)
        print(f'  - {item['name']}')


# global
call_count = 0

def get_urls(film6, kind, local_count):
    urls = film6[kind]
    print(kind)

def main():
    global call_count

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)

    items = ['characters', 'planets', 'starships', 'vehicles', 'species']
    threads = []

    for item in items:
        t = RequestKind(film6, item)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
        call_count += t.local_count

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
