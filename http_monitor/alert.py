from collections import deque
from datetime import datetime

class HitsCounter:
    def __init__(self, time):
        '''
        Object to keep track of time and count of hits for 2-minute window
        '''
        self.time = time
        self.counter = 1

class Alerter:
    def __init__(self, threshold):
        '''
        Set default values upon Alerter initiation
        '''
        self.total_hits = 0
        self.queue = deque()
        self.queue_dict = dict()
        self.on_alert = False
        self.threshold = threshold

    def _get_alert(self, row):
        '''
        inputs:
        - observation as common log format
        outputs:
        - if there is an alert: alert_start (boolean, True if start of alert, False if end),
          number of hits and time
        - if there is no alert: None

        Whenever average traffic for the past 2 minutes exceeds a certain
        threshold (default = 10/sec), print an alert to the console and log file.

        The main data structure to hold this information is a queue holding
        an object that stores the date (time in seconds) and a counter of how
        many hits were observed. The queue ensures a FIFO order to keep track
        of a 2 minute sliding window, where left-most items are the 'oldest'
        and right-most items the 'newest'.

        A dictionary keeps track of the same objects using the time as keys.
        This ensures to be able to edit the counter even if the time observed
        lies further ahead in the queue, since the data may not be in order.

        The number of total hits is updated with each observation:
        total_hits = total_hits + new - expired

        New observations are added and expired observations (older than 2 minutes)
        are deleted from the queue and the dictionary.

        The time for an alert recovery is computed by keeping track of whether
        the alert recovers when removing earlier items from the queue.
        '''

        # increase total alerts counter
        self.total_hits += 1
        # get the time from the observation for code readability
        time = int(row[3])

        # if observation for this time already exists, increase the counter
        if time in self.queue_dict:
            self.queue_dict[time].counter += 1
        # else add to dictionary & append to queue
        else:
            hits_counter = HitsCounter(time)
            self.queue.append(hits_counter)
            self.queue_dict[time] = hits_counter

        # delete expired from queue (older than current - 120sec)
        oldest_hit_counter = self.queue[0]  # peek, not pop
        end_alert_time = None
        while oldest_hit_counter.time < time - 120:
            # update total alerts by subtracting the alert counts from previous time
            self.total_hits -= oldest_hit_counter.counter
            # delete time entry from dictionary
            del self.queue_dict[oldest_hit_counter.time]
            # delete time entry from queue
            self.queue.popleft()

            # check if removing from queue would stop the alert and save time for later
            # subtract 1 to neglect current observation
            if not end_alert_time and (self.total_hits - 1) / 120 < self.threshold:
                # add 120 since the alert would end 2min after the high hits
                end_alert_time = oldest_hit_counter.time + 120

            oldest_hit_counter = self.queue[0]

        # updated total alerts counter of last 2 minutes
        hit_average = self.total_hits / 120  # average hits per second

        # send alert if average is larger than threshold,
        # and if there is no other alert active
        if self.threshold < hit_average and not self.on_alert:
            self.on_alert = True
            return True, self.total_hits, time

        # alert recovers if average is smaller than threshold, and a previous
        # alert is active (return end_alert_time from previous alert end)
        elif hit_average < self.threshold and self.on_alert:
            self.on_alert = False
            return False, self.total_hits, end_alert_time

        # if there is nothing to report, don't send an alert
        else:
            return None


    def get_alert_report(self, row):
        '''
        Returns the formatted output from check_alert
        '''
        alert = self._get_alert(row)
        if alert:
            alert_start, hits, time = alert
            timestring = datetime.utcfromtimestamp(int(time)).strftime("%Y-%m-%d %H:%M:%S")
            if alert_start:
                formatted_alert = (
                    f'High traffic generated an alert \n'
                    f'hits: \t {hits} ({round(hits/120, 2)}/sec) \n'
                    f'time: \t {timestring} \n')
                return formatted_alert
            else:
                formatted_alert = (
                    f'Alert ended at time: {timestring} \n')
                return formatted_alert

        else:
            return None
