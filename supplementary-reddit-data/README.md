# Supplementary Reddit Data Script:

The currently functional script is **batch_processing_script.py**. However, as this process was originally intended to subscribe and publish to Pulsar topics, there is also a **stream_processing_script.py** that is not yet fully functional, but is provided to demonstrate intended functionality.

## Batch Processing Script

### 0. Install Correct Python Version:

[![made-with-python](https://img.shields.io/badge/python-3.7.0-blue.svg)](https://www.python.org/)

### 1. Install **dependencies**:
1. Navigate to `reddit-sentiment-analysis/supplementary-reddit-data/src`
2. Run `$ pip install -r requirements.txt`

:white_check_mark:  You should now have `praw` and `dask` installed

### 2. Acquire and set up **OAuth Credentials**:
1. _(create Reddit Account if you do not have one yet)_
2. Follow the "**Getting Started**" instructions here: [https://github.com/reddit-archive/reddit/wiki/OAuth2](https://github.com/reddit-archive/reddit/wiki/OAuth2)
3. Create a `praw.ini` file in `reddit-sentiment-analysis/supplementary-reddit-data/src` and include your credentials like so:
```
[supplementary-reddit-data]
client_id=fake-client-id
client_secret=fake-client-secret
user_agent=supplementary-reddit-data-script:v1.0.0 (by /u/your-username)
```
Make sure to name the 'site' the same way (see first line above) so that the script will be able to reference your credentials.  

:white_check_mark:  You are now set up to call Reddit's API

### 3. Acquire input file(s)
A sample input file has been provided for your convenience in `reddit-sentiment-analysis/supplementary-reddit-data/input-data`  

Format of input file:
- **Named**: `<BATCH_NAME>.json`
- **Contains**: one JSON record per line.
    - JSON data is result of Sentiment Analysis Processing
    - Only _required_ field is `"author"`
    - Sample:
    ```
    {
        "author": "Fafnirsfriend",
        "author_flair_css_class": "None",
        "author_flair_text": "None",
        "can_gild": "True",
        "controversiality": 0,
        "created_utc": 1512086400,
        "distinguished": "None",
        "edited": "False",
        "gilded": 0,
        "id": "dql1dzt",
        "is_submitter": "False",
        "link_id": "t3_7gojgh",
        "parent_id": "t1_dqkz1pz",
        "permalink": "/r/books/comments/7gojgh/fahrenheit_451_this_passage_in_which_captain/dql1dzt/",
        "retrieved_on": 1514212661,
        "score": 12,
        "stickied": "False",
        "subreddit": "books",
        "subreddit_id": "t5_2qh4i",
        "subreddit_type": "public",
        "sentiment": 0.046875
    }
    ```
### 4. Prepare output directory (if one doesn't already exist):
1. Navigate back to `reddit-sentiment-analysis/supplementary-reddit-data`
2. Create directory `output-data`. This is where the processed data will be stored.

### 5. You are now ready to run the script! :thumbsup:
1. Navigate to `/src`
2. run `$ python3 batch_processing_script.py [BATCH-NAME]`  
    (i.e.) `$ python3 batch_processing_script.py batch-000` to run the provided sample file

Output to console should be logging basic stats (for debugging) and progress of threaded processes.

Once program is finished, navigate to your output directory (`../output-data`) and check the file with the name of the batch you just processed (`[BATCH-NAME].json`).
