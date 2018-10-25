from utils import run_with_threads, update_user_data_and_mids_queue

if __name__ == '__main__':
    uids = list()
    with open('uids.txt', 'r') as f:
        for line in f:
            uids.append(line.strip())

    run_with_threads(update_user_data_and_mids_queue, uids, 100)
