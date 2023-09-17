import asyncio
import datetime

import pandas
import pytz
import redis

from django_emailing_server import logger

DJANGO_UPDATES_INTERVAL = 15


def redis_connection():
    conn = redis.Redis('redis', 6379, password=None)
    try:
        conn.ping()
    except:
        logger.critical('Could not log in to Redis backend')
        return False
    return conn


async def localized_current_date(timezone):
    timezone = pytz.timezone(timezone)
    return datetime.datetime.now(tz=timezone)


def convert_date(date_string, timezone=None):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f%z')


async def calculate_date_intervals(start_date, interval, timezone=pytz.UTC, leads_per_day=10):
    dates = []
    d = convert_date(start_date, timezone=timezone)
    # Always start the next day because if we
    # start right now, the current date moves
    # while the tasks are created which makes
    # that the difference between the current
    # date and the execution day of the task will
    # not be exactly the number of the intervall
    next_day = datetime.timedelta(days=1) + d
    for _ in range(leads_per_day):
        if not dates:
            result = datetime.timedelta(minutes=interval) + next_day
        else:
            result = datetime.timedelta(minutes=15) + dates[-1]
        dates.append(result)
    return dates


async def email_task(email, execution_date, sequence):
    async def sender():
        has_to_wait = True
        while has_to_wait:
            current_date = await localized_current_date('UTC')
            if current_date >= execution_date:
                print(
                    'current_date', str(current_date),
                    'execution_date', str(execution_date)
                )
                # print('Send email', email, sequence)
                has_to_wait = False
            print('For', email, execution_date)
            await asyncio.sleep(5)
    return await asyncio.ensure_future(sender())


async def create_sending_tasks(sequences):
    tasks = []
    for sequence in sequences:
        dates = await calculate_date_intervals(sequence['start_date'], sequence['interval'])
        emails = ['1', '2']
        for i, email in enumerate(emails):
            task = asyncio.create_task(email_task(
                email, dates[i],
                sequence),
                name=f'task_for_{email}'
            )
            tasks.append(task)
    return tasks


async def main():
    logger.info('Starting email server')

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
                sequence_keys = conn.lrange('sequence_keys', 0, -1)
                for key in sequence_keys:
                    decoded_key = key.decode()
                    sequence_details = conn.get(decoded_key)
                    # Get the current sending calendar that
                    # was calculated in order to determine
                    # the sending dates for each tasks
                    if sequence_details is not None and sequence_details['active']:
                        sending_calendar = conn.hget(
                            'calendars',
                            sequence_details['sequence_id']
                        )
                        if sending_calendar is None:
                            date_intervals = await calculate_date_intervals(
                                sequence_details['start_date'],
                                sequence_details['interval']
                            )
                            conn.hset(
                                'calendars',
                                sequence_details['sequence_id'],
                                date_intervals
                            )
                        await campaign_queue.put(sequence_details)
                    logger.info(f'Found {len(sequence_keys)} sequences')
            await asyncio.sleep(5)

    await asyncio.gather(redis_poller())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Stopping server')
    except Exception as e:
        logger.error(e)
