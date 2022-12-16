import tempfile
import datetime
import time
import json


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def setup_temp_file(items_total, items_done):
    temp = tempfile.NamedTemporaryFile()
    setup = {
        'start_time': int(time.time()),
        'items_total': items_total,
        'items_done': items_done
    }
    with open(temp.name, 'w') as file_out:
        json.dump(setup, file_out)

    return temp


def setup_progress_dict(items_total, items_done):
    setup = {
        'start_time': int(time.time()),
        'items_total': items_total,
        'items_done': items_done
    }

    return setup


def check_progress(temp_file, items_completed):
    current_time = int(time.time())

    with open(temp_file, 'r') as file_in:
        setup = json.load(file_in)

    num_completed_since_start = abs(items_completed - setup['items_done'])

    if num_completed_since_start != 0:
        time_per_item = (current_time - setup['start_time']) / num_completed_since_start
    else:
        time_per_item = 0

    seconds_left = time_per_item * (setup['items_total'] - items_completed)

    iteration = items_completed

    start_time = datetime.datetime.fromtimestamp(setup['start_time'])

    prefix = datetime.datetime.strftime(start_time, "%d/%m/%y %H:%M:%S")

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_left)

    suffix = datetime.datetime.strftime(end_time, "%d/%m/%y %H:%M:%S.")

    printProgressBar(iteration, setup['items_total'], prefix=prefix, suffix=suffix)


def check_progress_dict(setup, items_completed):
    current_time = int(time.time())

    num_completed_since_start = abs(items_completed - setup['items_done'])

    if num_completed_since_start != 0:
        time_per_item = (current_time - setup['start_time']) / num_completed_since_start
    else:
        time_per_item = 0

    seconds_left = time_per_item * (setup['items_total'] - items_completed)

    iteration = items_completed

    start_time = datetime.datetime.fromtimestamp(setup['start_time'])

    prefix = datetime.datetime.strftime(start_time, "%d/%m/%y %H:%M:%S")

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_left)

    suffix = datetime.datetime.strftime(end_time, "%d/%m/%y %H:%M:%S.")

    printProgressBar(iteration, setup['items_total'], prefix=prefix, suffix=suffix)
