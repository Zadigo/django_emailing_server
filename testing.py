import datetime
import time
import pandas
import pytz

CAMPAIGNS = [
    {
        'id': 'seq_12345',
        'timezone': 'UTC',
        'start_date': '2023-09-14 12:53:10.456377+00:00',
        'last_execution': None,
        'next_execution': None,
        'wait_for': 5,
        'interval': 15,
    }
]


def localized_current_date(timzone):
    timzone = pytz.timezone(timzone)
    return datetime.datetime.now(tz=timzone)


def convert_date(date_string, timezone=None):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f%z')


def difference_in_minutes(d1, d2, round_to=3):
    d1 = convert_date(d1)
    d2 = convert_date(d2)
    result = (d2 - d1).total_seconds()
    return round(result / 60, round_to)


while True:
    current_date = None

    df = pandas.DataFrame(CAMPAIGNS)

    if current_date is None:
        current_date = datetime.datetime.now(tz=pytz.UTC)

    # Only work with the sequences that are
    # supposed to be run for today
    sequences_to_run_today = df[df['start_date'] > str(current_date.date())]

    if sequences_to_run_today.empty:
        continue

    for item in df.iterrows():
        index, series = item
        campaign_date = convert_date(series.start_date)
        current_date = localized_current_date(series.timezone)

        last_execution_date_string = df.last_execution.iloc[index]
        if last_execution_date_string is None:
            print('Start initial sequence execution')
            df.iloc[index].last_execution = str(current_date)
            continue

        last_execution = convert_date(df.last_execution.iloc[index])
        number_of_minutes = difference_in_minutes(last_execution, current_date)
        if number_of_minutes >= df.interval.iloc[index]:
            print('Send email')
        print('Execute sequence')
        df.iloc[index].last_execution = str(current_date)

    data = df.to_json(orient='records')
    print(data)
    # Save this information in Redis which will be
    # be sent to Django every 15 minutes
    print({'execution_date': current_date, 'campaign_id': None, 'sequence_id': None, 'action': 'Sent', 'success': False, 'error': None})
    time.sleep(30)
