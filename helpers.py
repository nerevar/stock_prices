from datetime import timedelta

DATE_FORMAT = '%Y-%m-%d'


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
