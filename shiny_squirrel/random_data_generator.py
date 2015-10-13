import random
import time

import requests


def main():
    total = 0
    while True:
        data = {'totals': {'all': total}}
        requests.post('http://localhost:5000/totals', json=data)
        total = total + random.randint(1, 15)
        time.sleep(random.random()+0.25)


if __name__ == '__main__':
    main()
