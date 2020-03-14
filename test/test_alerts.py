import unittest
from http_monitor.alert import Alerter
from collections import deque
import random

class TestAnalyticsMethods(unittest.TestCase):

    def test_alert_start(self):
        alerter = Alerter(10)
        test_row = ['10.0.0.3', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '200', '1234']
        for i in range(1200):
            alerter._get_alert(test_row)

        result = (True, 1201, 1549573860)
        self.assertEqual(alerter._get_alert(test_row), result)

    def test_alert_end(self):
        alerter = Alerter(10)
        # add 1201 hits at the same time
        test_row = ['10.0.0.3', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '200', '1234']
        for i in range(1201):
            alerter._get_alert(test_row)

        # add a new hit 130 seconds later (new time = test time + 130 = 1549573990)
        row = ['10.0.0.3', '-', 'apache', '1549573990', 'POST /report HTTP/1.0', '200', '1234']

        # time the alert should be generated: test time + 120 = 1549573980
        result = (False, 1, 1549573980)
        self.assertEqual(alerter._get_alert(row), result)

    def test_alert_none(self):
        alerter = Alerter(10)
        test_row = ['10.0.0.3', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '200', '1234']
        for i in range(200):
            alerter._get_alert(test_row)
        result = None
        self.assertEqual(alerter._get_alert(test_row), result)

    def test_alert_unordered(self):
        alerter = Alerter(10)
        test_row = ['10.0.0.3', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '200', '1234']
        # for each second
        for i in range(120):
            # create 10 alerts +/- 1 or 2 seconds
            for i in range(10):
                time = 1549573860 + random.choice([-1, -2, 0, 1, 2])
                test_row[3] = str(time)
                alerter._get_alert(test_row)
        # final observation 120 seconds later
        test_row = ['10.0.0.3', '-', 'apache', '1549573980', 'POST /report HTTP/1.0', '200', '1234']
        result = (True, 1201, 1549573980)
        self.assertEqual(alerter._get_alert(test_row), result)

if __name__ == '__main__':
    unittest.main()
