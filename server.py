import asyncio
import datetime

import pandas
import redis

from django_emailing_server import logger

DJANGO_UPDATES_INTERVAL = 15


def redis_connection():
    conn = redis.Redis('redis', 6379, password=None)
    try:
        conn.ping()
    except:
        print('Cannot log to Redis')
        return False
    return conn


async def main():
    campaign_queue = asyncio.Queue()
    conn = redis_connection()

    async def email_sender():
        while True:
            while not campaign_queue.empty():
                pass

    async def django_updater():
        current_date = None
        while True:
            if current_date is None:
                current_date = datetime.datetime.now()

            updated_date = datetime.datetime.now()
            difference = (updated_date - current_date)
            minutes = difference.total_seconds() / 60

            if minutes >= DJANGO_UPDATES_INTERVAL:
                print('Update Django')
                current_date = updated_date
            await asyncio.sleep(10)

    async def redis_poller():
        while True:
            if conn:
                campaign_keys = conn.lrange('campaign_keys', 0, -1)
                for key in campaign_keys:
                    key.decode('utf-8')
                    campaign_details = conn.get(key)
                    if campaign_details['active']:
                        await campaign_queue.put(campaign_details)
                    print(campaign_details)
            await asyncio.sleep(5)

    await asyncio.gather(redis_poller(), django_updater())


if __name__ == '__main__':
    asyncio.run(main())
