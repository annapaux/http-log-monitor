##########################################################################
# Imports and Settings
##########################################################################
import csv
import os

# Logging
import logging, sys
# basic config to log file (DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs.log',
                    filemode='w')  # overwrite existing file
# add handler to log to console stream (INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# internal
from http_monitor.analytics import get_analytics_report
from http_monitor.alert import Alerter


##########################################################################
# Main
##########################################################################

if __name__ == '__main__':
    '''
    - reads line-by-line input from log file
    - generates analytics report after 10 seconds
    - alerts if rolling average over 2 minutes exceeds a threshold

    Row in log-file:
    ['remotehost', 'rfc931', 'authuser', 'date', 'request', 'status', 'bytes']
    '''

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-log_path',
            type=str,
            help='path to log file, default: data/sample_csv.txt',
            default = 'data/sample_csv.txt')
    parser.add_argument(
            '-threshold',
            type=int,
            help='alert threshold (hits/second), default: 10',
            default=10)
    args = parser.parse_args()


    # read input
    with open(args.log_path) as f:
        csv_reader = csv.reader(f, delimiter=',')
        first_row = True
        counter = 0

        # 10 seconds analytics
        interval_start = None
        interval_data = []

        # rolling 2 minute alert
        threshold = args.threshold  # change as needed
        alerter = Alerter(threshold)


        # iterate over each row observation
        for row in csv_reader:

            # if first row, get column names (header)
            if first_row:
                header = row
                first_row = False

            # all other observations
            else:

                ##########################
                # 2-minute rolling alert
                ##########################

                # start 2-minute rolling alerts
                formatted_alert = alerter.get_alert_report(row)
                if formatted_alert:
                    logging.info(f'Alert \n' +
                                f'{formatted_alert}')

                ##########################
                # 10 seconds analytics
                ##########################

                # initiate interval_start of first observation
                if not interval_start:
                    interval_start = int(row[3])

                # if it's in the same interval, add data
                if int(row[3]) <= interval_start + 10:
                    interval_data.append(row)

                # if it's a new interval, print data and start new interval
                else:
                    analytics = get_analytics_report(interval_start, header, interval_data)
                    logging.info(f'Analytics \n{analytics}')

                    # re-set 10 second analytics
                    interval_data = []
                    interval_start += 10

                    # if there are no errors for some intervals, log 'no errors'
                    while interval_start + 10 < int(row[3]):
                        logging.info(f'No errors to log at time {interval_start}.')
                        interval_start += 10

                    # add data to 10-second analytics
                    interval_data.append(row)
