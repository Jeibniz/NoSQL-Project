"""
NAME:   SUPPLEMENTARY REDDIT DATA BATCH PROCESSING SCRIPT

ABOUT:  Script batch processes Reddit Comment JSON data from text files
        (post Sentiment Analysis), acquires additional Reddit information
        (via RedditClient), and write batch results to another text file.

AUTHOR: Julia Garbuz (garbu007@umn.edu)
"""

import dask
import logging
from multiprocessing.pool import ThreadPool
import datetime
import sys

from supplementary_reddit_data_service.supplementary_reddit_data_service \
    import SupplementaryRedditDataService


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SOURCE/DEST FILE CONFIGURATION:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
__BATCH_NAME = str(sys.argv[1])

__IN_FILE = "../input-data/" + __BATCH_NAME + ".json"
__OUT_FILE = "../output-data/" + __BATCH_NAME + ".json"


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
BATCH SIZE CONFIGS:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Reddit limits to < 12 parallel instances, so max is set to 10
def get_num_sub_batches(total_batch_size):
    if total_batch_size >= 10: return 10
    else: return total_batch_size


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
LOGGER CONFIG/METHODS:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
__SHOW_LOGS = True

# Larger batches take significantly longer to process, so wanted
# to have more frequent checkpoints
def get_progress_checkpoint(sub_batch_size):
    if sub_batch_size < 100: return 10
    if sub_batch_size < 1000: return 50
    if sub_batch_size < 10000: return 100
    else: return 1000

def batch_name(batch_id):
    return "\t\t(SUB BATCH #" + str(batch_id) + ")"

def init_log(batch_id, start_idx, end_idx):
    return batch_name(batch_id) + " ––> [INIT]: Index Range [" + \
           str(start_idx) + ", " + str(end_idx) + ")"

def progress_log(batch_id, percent_complete):
    return batch_name(batch_id) +\
           " ––> [PROCESSING]: " + \
           format(percent_complete, '.2f') + "%"


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SUB-BATCH PROCESSING METHOD:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@dask.delayed
def process_sub_batch(sub_batch, batch_id):
    logging.info(batch_name(batch_id) + " ––> [START]")

    # NOTE: PRAW Reddit instances are not thread safe so avoid errors by
    # creating new service (and therefore Reddit) instance for each
    # parallel-processed batch
    service = SupplementaryRedditDataService()

    processed_sub_batch = []

    len_sub_batch = len(sub_batch)
    progress_checkpoint = get_progress_checkpoint(len_sub_batch)

    # For each sub-batch
    for data_idx in range(len_sub_batch):

        # Process sub-batch and append to "processed" list
        processed_sub_batch.append(
            service.add_supplementary_reddit_data(sub_batch[data_idx])
        )

        # Log (debug/progress print) if satisfies checkpoint condition:
        if data_idx % progress_checkpoint == 0:
            percent_complete = (data_idx/len_sub_batch)*100
            logging.info(progress_log(batch_id, percent_complete))

    logging.info(batch_name(batch_id) + " ––> [END]")
    return processed_sub_batch


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MAIN PROCESSING SCRIPT:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
if __name__ == '__main__':

    start_time = datetime.datetime.now() # for stats/metadata (processing time)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    (1) Configure logger
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    if __SHOW_LOGS: logging.basicConfig(format='%(asctime)s %(message)s',
                                        datefmt='%m/%d/%Y %I:%M:%S %p',
                                        level=logging.INFO)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    (2) Read IN_FILE, split data into sub-batches
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    with open(__IN_FILE, 'r') as infile:
        all_lines = infile.readlines()

        num_lines = len(all_lines)
        logging.info("Number of lines in IN_FILE: " + str(num_lines))
        logging.info("Total Index Range: [0, " + str(num_lines-1) + "]")

        num_sub_batches = get_num_sub_batches(num_lines)
        logging.info("Number of Sub-Batches: " + str(num_sub_batches))

        sub_batch_len = num_lines // num_sub_batches
        logging.info("Sub-Batch Length: " + str(sub_batch_len))

        all_sub_batches = []

        batch_num = 0
        sub_batch_start_idx, sub_batch_end_idx = 0, 0
        while sub_batch_start_idx < num_lines:
            sub_batch_end_idx = sub_batch_start_idx + sub_batch_len

            # Include "overflow" into last batch
            if (num_lines - sub_batch_end_idx) < sub_batch_len:
                sub_batch_end_idx = num_lines

            logging.info(
                init_log(batch_num, sub_batch_start_idx, sub_batch_end_idx)
            )
            sub_batch = all_lines[sub_batch_start_idx : sub_batch_end_idx]

            all_sub_batches.append(sub_batch)
            sub_batch_start_idx = sub_batch_end_idx

            batch_num += 1

    logging.info("[√] SET UP COMPLETE")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    (3) Generate tasks for each batch, and 'compute' (perform task)
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    with dask.config.set(scheduler='processes', pool=ThreadPool(10)):
        tasks = []

        for i in range(num_sub_batches):
            new_sub_batch = process_sub_batch(all_sub_batches[i], i)
            tasks.append(new_sub_batch)

        result = dask.delayed()(tasks).compute()

    logging.info("[√] PROCESSING COMPLETE")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    (4) Write result of tasks to file and accumulate stats:
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    with open(__OUT_FILE, 'w') as outfile:
        num_records_written = 0
        num_records_dropped = 0

        for sub_batch in result:

            for data in sub_batch:

                num_records_written += 1

                if data == "DROPPED\n":
                    num_records_dropped += 1

                outfile.write(data)

    end_time = datetime.datetime.now()
    logging.info("[√] WRITING COMPLETE")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    (5) Log stats (alternatively could write metadata to file)
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    logging.info("Records READ from IN_FILE:\t" + str(num_lines))
    logging.info("Records WRITTEN to OUT_FILE:\t" + str(num_records_written))
    logging.info("Records DROPPED:\t\t\t" + str(num_records_dropped))
    logging.info("Time to Complete:\t\t" + str(end_time - start_time))
