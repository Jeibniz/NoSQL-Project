# Sentiment Reddit Data Script:
The currently functional script is sentiment_analysis_load_json_file.py. Because the original design was for this process to subscribe and publish to Pulsar topics, there is also a sentiment_analysis_pulsar.py that is not yet fully functional for a production-level distribution of pulsar, but is provided to demonstrate intended functionality.

## Batch Processing Script
### 1. Make sure python3 is installed
-there are not any additional packages that need to be installed


### 2. Acquire sentiment word level lexicon text file
-the file NRC-Emotion-Lexicon-Wordlevel-v0.92.txt in GIT can be placed in a "sentiment" subfolder within the "/sentiment_analysis" parent folder


### 3. Acquire input file
A sample input file has been provided in the "sentiment_analysis" folder in GIT.

Format of input file:

- **Named**: sentiment_sample.json
- **Contains**: one JSON record per line.
    - JSON data is the input
    - Only required field is "author"
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
        "body": "this is an excellent sample"
    }
    ```

### 4. Prepare output directory:
The output will be placed in the same folder as the python script (i.e. "sentiment_analysis"). 


### 5. You are now ready to run the script!
-Navigate to /sentiment_analysis
-Run $ python3 sentiment_analysis_load_json_file.py
-Output to console is optional. It's currently commented out (line 157) and will display the processed record when uncommented.

Once program is finished, navigate to /sentiment_analysis (../out) and check the file with the name of the file (sentiment_added.json)
