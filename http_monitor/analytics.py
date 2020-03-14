import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
from datetime import datetime

##########################################################################
# Tools
##########################################################################

def _pre_process(interval_start, header, interval_data):
    '''
    adds section and request type column to interval data
    '''
    df = pd.DataFrame(np.array(interval_data), columns=header)
    df['section'] = df.apply(lambda row:
                                row.request.split('/')[1].split(' ')[0], axis=1)
    df['request_type'] = df.apply(lambda row:
                                row.request.split()[0], axis=1)
    return df


def _get_most_hits(df):
    '''
    returns section and count of hits
    '''
    hits_count = df['section'].value_counts()
    hits_section = hits_count.index.tolist()
    hits_value = hits_count.tolist()
    return hits_section, hits_value


def _get_most_hits_details(df):
    '''
    returns detail view of top 5 most hits as pandas dataframe
    '''
    hits_details = df.groupby(['section', 'request_type', 'remotehost']) \
                                .size() \
                                .reset_index(name='count') \
                                .sort_values(['count'], ascending=False)
    return hits_details[:5]


def _get_error_status(df):
    '''
    returns pandas dataframe of top 5 error status and count
    '''
    # errors & their platforms
    not_200 = df['status'] != '200'
    temp = df[not_200]
    top_errors = temp.groupby(['status', 'remotehost']) \
                                .size() \
                                .reset_index(name='count') \
                                .sort_values(['count'], ascending=False)
    top_errors.index = np.arange(1, len(top_errors)+1)
    top_errors = top_errors[:5]
    return top_errors


def _get_bytes_stats(df):
    '''
    returns descriptive statistics about bytes load
    '''
    bytes_num = pd.to_numeric(df['bytes'])
    mean = round(bytes_num.mean(), 2)
    std = round(bytes_num.std(), 2)
    max_ = bytes_num.max()
    return mean, std, max_
    # return np.round(pd.to_numeric(df['bytes']).describe(), 2)


##########################################################################
# Main
##########################################################################

def get_analytics_report(interval_start, header, interval_data):
    '''
    returns formatted analytics as a string
    includes all analytics from tools above
    '''

    # pre-process the data
    start_time = datetime.utcfromtimestamp(int(interval_start)).strftime("%Y-%m-%d %H:%M:%S")
    df = _pre_process(interval_start, header, interval_data)

    # sections with most hits
    hits_section, hits_value = _get_most_hits(df)
    most_hits = ''
    for i in range(min(3, len(hits_section))):
        most_hits = most_hits + f'({i+1}) {hits_section[i]}: {hits_value[i]} \n'

    # print(repr(most_hits))

    # details of highest hits
    most_hits_details = _get_most_hits_details(df)

    # errors & their platforms
    top_errors = _get_error_status(df)
    # print(repr(top_errors.to_string()))

    # bytes stats
    byte_mean, byte_std, byte_max_ = _get_bytes_stats(df)


    analytics = (
    f'10-Second Report \n'
    f'Start time: {start_time} \n'
    f'Total number of hits: {len(interval_data)} \n'
    '\n'

    f'Most hits: \n'
    f'{most_hits} \n'

    f'Top 5 most hits details: \n'
    f'{most_hits_details} \n'
    f'\n'

    f'Top 5 errors by status code: \n'
    f'{top_errors} \n'
    f'\n'

    f'Bytes Load: \n'
    f'mean: \t {byte_mean} \n'
    f'std: \t {byte_std} \n'
    f'max: \t {byte_max_} \n'
    )
    return analytics

if __name__ == '__main__':
    header = ['remotehost', 'rfc931', 'authuser', 'date', 'request', 'status', 'bytes']
    interval_data = [['10.0.0.2', '-', 'apache', '1549573860', 'GET /api/user HTTP/1.0', '200', '1234'],
    ['10.0.0.4', '-', 'apache', '1549573860', 'GET /api/user HTTP/1.0', '200', '1234'],
    ['10.0.0.4', '-', 'apache', '1549573860', 'GET /api/user HTTP/1.0', '200', '1234'],
    ['10.0.0.2', '-', 'apache', '1549573860', 'GET /api/help HTTP/1.0', '200', '1234'],
    ['10.0.0.5', '-', 'apache', '1549573860', 'GET /api/help HTTP/1.0', '200', '1234'],
    ['10.0.0.4', '-', 'apache', '1549573859', 'GET /api/help HTTP/1.0', '200', '1234'],
    ['10.0.0.5', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '500', '1307'],
    ['10.0.0.3', '-', 'apache', '1549573860', 'POST /report HTTP/1.0', '200', '1234'],
    ['10.0.0.3', '-', 'apache', '1549573860', 'GET /report HTTP/1.0', '200', '1194']]
    interval_start = '1549573860'

    # result = get_analytics_report(interval_start, header, interval_data)
    # print(result)

    start_time = datetime.utcfromtimestamp(int(interval_start)).strftime("%Y-%m-%d %H:%M:%S")
    df = _pre_process(interval_start, header, interval_data)
    result = _get_most_hits_details(df)

    print(repr(result.to_string()))
