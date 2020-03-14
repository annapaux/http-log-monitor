# HTTP Traffic Monitor
This program monitors HTTP traffic given a file of HTTP logs in common log format.

### Set Up
This app runs on Python 3.6.

1) set the `http_monitor` as the current working directory
2) To install all requirements run `pip install -r /path/to/requirements.txt` from the terminal.
3) Run the file via `python main.py -log_path path/to/data.txt -threshold threshold_integer`. The parameters are optional with the following defaults: `python main.py -log_path data/sample_csv.txt -threshold 10`

All commands:
```
python3 -m venv http_venv
source http_venv/bin/activate
cd path/to/http_monitor
pip install -r requirements.txt
python main.py
```

### Main File
The main file reads the data line by line and calls the `alert.py` and `analytics.py` files for the alerts and statistics, respectively. Alerts and statistics are logged to the console and the `logs.log` file.
As an input, it takes a csv formatted .txt file, where each row has the common log format: 'remotehost', 'rfc931', 'authuser', 'date', 'request', 'status', 'bytes'. For example: "10.0.0.2", "-", "apache", 1549573860, "GET /api/user HTTP/1.0", 200,1234 .


### Alerts
A rolling 2-minute window is used to count the number of hits and evaluate whether an alert should be generated. If the average count of alerts exceeds a threshold (default is 10 hits per second on average), an alert is generated and logged to the console. Once the average is below the threshold, a message is logged to announce the recovery of the alert. The recovery is only triggered upon seeing the 'next' observation. For example, if an alert is triggered at t=0, the next observation is for t=140, then the recovery is triggered upon reading the next observation, but prints the correct recovery time (e.g. t=120).

The main data structure holding this information is a first-in-first-out queue to keep the order and a sliding 2-minute window, as well as a dictionary to keep track of hit counters even if the data is unordered.


### Analytics
The analytics are performed for a 10 second interval, starting with the time of the first observation and for all 10 second intervals after that. If there is no observation within 10 seconds, a message stating that is printed.

The `main.py` file reads the input, stores the data for 10 seconds in memory and calls the `analytics.py` file to analyze all the events that happened in the past 10 seconds. The `analytics.py` file gathers all information and creates a string of information, which is in the `get_analytics_report.py` function.

Current analytics:
- sections with most hits
- detail view including section, request_type, remotehost and count
- error status with highest count
- bytes load stats (mean, std, max)


### Notes
- The log file currently gets overwritten at each run. If instead the output should be appended, change the filemode parameter in the basicConfig to 'a'.
- The functions to get analytics and alerts have value based and formatted versions. This separation is to allow formatting-neutral test cases while also abstracting the formatting from the main code.
- This program assumes that the log file is roughly ordered by date. Since the queue is limited to a 2-minute window, the first observation of a 'future' time kicks out the time observations 2 minutes prior to the event. If the data is grossly out of order, so will be the queue. More on the implementation in the `alert.py` file and on weaknesses and improvements in the improvements section below.


### Improvements
- The current implementation requires a static data input file. This could be improved with a while loop that reads from an actively written to file file and sleeps when there is no new line.
- Currently, data for the previous 10 seconds is stored in memory as a list of all data in the past 10 seconds. If a lot of errors occur within the 10 seconds, this file can grow very large. Instead, statistics could be stored and updated after each observation. This will be particularly valuable as the application scales and more logs per second occur. Alternatively, a database could be used to store the observations.
- The sample data is slightly out of order, though only varying by 2 seconds (see `data/explore_data.py`). The current implementation optimizes for this 'slightly-out-of-order' data by using a queue and dictionary to access previous values. However, a cleaner implementation would be valuable, either by sorting the data in advance, which takes at least O(NlogN), or adapting the implementation to work with unsorted data. A weakness of the current implementation is that if first future dates appear before previous (e.g. 1,1,3,2), then the queue is out of order and the alert and analytics may report be wrong. In addition, the first occurrence of a time 'kicks out' observations 120 seconds prior, and triggers alerts/analytics even though statistics up until and including this time frame may still appear later. Unless there is some guarantee of order, I couldn't think of a solution that works efficiently without scanning the entire file and storing the observations in a database, to then perform analytics and alerts on. Space for improvement on this front.
- The current analytics are very basic and largely performed via the pandas library. This can be improved by considering what the crucial statistics are, how to best visualize them and whether there are more efficient ways other than pandas. For example, some form of anomaly detection to previous data would be very interesting.


### Tests
To run the alerts unit tests, run
`python -m unittest test_alerts.py`
or to run all tests run
`python -m unittest discover`




Author: Anna Pauxberger
Date: 04 March 2020
Project: Datadog Take-Home Project
