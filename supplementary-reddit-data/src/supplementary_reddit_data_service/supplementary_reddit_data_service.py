""" AUTHOR: Julia Garbuz (garbu007@umn.edu) """

import json
from reddit_client.reddit_client import RedditClient
from reddit_client.user_not_found_exception import UserNotFoundException
from reddit_client.no_created_utc_exception import NoCreatedUTCException

class SupplementaryRedditDataService:
    """
    SupplementaryRedditDataService implements core functionality of application
    (accepts JSON, adds supplementary data, returns updated JSON)
    """

    def __init__(self):
        self.__reddit_client = RedditClient()

    def add_supplementary_reddit_data(self, json_as_string):
        data = json.loads(json_as_string)
        if data and 'author' in data:
            author = data['author']

            # 3 POSSIBLE OUTCOMES OF CALLING REDDIT'S API:

            try:
                # (1) USER SUCCESSFULLY FOUND WITH CREATED_UTC
                # --> pass record (with created_utc)
                data["user_created_utc"] = \
                    self.__reddit_client.get_user_created_utc(author)
                data["added_user_created_utc"] = True
                return json.dumps(data) + "\n"

            except UserNotFoundException:
                # (2) USER DELETED (no info found)
                # --> drop record
                return "DROPPED\n"

            except NoCreatedUTCException:
                # (3) USER SUSPENDED (found but with no created_utc)
                # --> pass record but flag lack of created_utc
                data["added_user_created_utc"] = False
                return json.dumps(data) + "\n"
