# Since the data is not in-order, this program explores to what extent this log file is out of order
# This affects processing for the alert file. 

first_row = True
time_dict = dict()  # {time: [first_occurrence, last_occurrence, highest_time_difference_inbetween]}
largest_date = 0

f = open('data/sample_csv.txt', 'r')
for row in f:
    if first_row:
        first_row = False
    else:
        data = row.split(',')
        date = int(data[3])
        if largest_date < date:
            largest_date = date
        if date in time_dict:
            time_dict[date][1] = date
            time_dict[date][2] = largest_date - date
        else:
            time_dict[date] = [date, date, 0]

max_difference = max(time_dict.values(), key=lambda x: x[2])
print(f'The maximum overlap between timestamps is: {max_difference[2]} seconds')
