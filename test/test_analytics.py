import unittest
from http_monitor.analytics import _pre_process, _get_most_hits, _get_most_hits_details, _get_error_status

class TestAnalyticsMethods(unittest.TestCase):

    header = ['remotehost', 'rfc931', 'authuser', 'date', 'request', 'status', 'bytes']
    interval_data = [
    ['10.0.0.2', '-', 'apache', '1549573860', 'GET /api/user HTTP/1.0', '200', '1234'],
    ['10.0.0.4', '-', 'apache', '1549573860', 'GET /api/user HTTP/1.0', '200', '1234'],
    ['10.0.0.4', '-', 'apache', '1549573860', 'GET /api/user HTTP/1.0', '200', '1234'],
    ['10.0.0.2', '-', 'apache', '1549573860', 'GET /api/help HTTP/1.0', '200', '1234'],
    ['10.0.0.5', '-', 'apache', '1549573860', 'GET /api/help HTTP/1.0', '200', '1234'],
    ['10.0.0.4', '-', 'apache', '1549573859', 'GET /api/help HTTP/1.0', '200', '1234'],
    ['10.0.0.5', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '500', '1307'],
    ['10.0.0.3', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '200', '1234'],
    ['10.0.0.3', '-', 'apache', '1549573860', 'GET /report HTTP/1.0', '200', '1194']]
    interval_start = '1549573860'
    df = _pre_process(interval_start, header, interval_data)


    def test_most_hits(self):
        result = (['api', 'report'], [6, 3])
        self.assertEqual(_get_most_hits(self.df),
            result)

    def test_most_hits_details(self):
        self.assertEqual(_get_most_hits_details(self.df).to_string(),
            ('  section request_type remotehost  count\n' +
            '1     api          GET   10.0.0.4      3\n' +
            '0     api          GET   10.0.0.2      2\n' +
            '2     api          GET   10.0.0.5      1\n' +
            '3  report          GET   10.0.0.3      1\n' +
            '4  report         POST   10.0.0.3      1'))

    def test_error_status(self):
        self.assertEqual(_get_error_status(self.df).to_string(),
            '  status remotehost  count\n1    500   10.0.0.5      1')


if __name__ == '__main__':
    unittest.main()
