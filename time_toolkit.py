import time


if __name__ == '__main__':
    time_string = 'Wed Mar 2 20:10:05 +0800 2018'

    # string to time_tuples
    time_tuples = time.strptime(time_string, "%a %b %d %H:%M:%S +0800 %Y")
    # time_tuples to timestamp
    timestamp = time.mktime(time_tuples)

    # time_tuples to string
    print(time.strftime('%Y-%m-%d %H:%M:%S', time_tuples))

    # timestamp to time_tuples
    print(time.localtime(timestamp))

    print(tuple(time_tuples))

    print(time.struct_time(tuple(time_tuples)))
