""" AUTHOR: Julia Garbuz (garbu007@umn.edu) """

import praw
import prawcore

from reddit_client.user_not_found_exception import UserNotFoundException
from reddit_client.no_created_utc_exception import NoCreatedUTCException


class RedditClient:
    """
    'RedditClient' uses PRAW ("Python Reddit API Wrapper") with Datanaut's
    Reddit API developer credentials (from 'praw.ini')
    """

    def __init__(self):
        """ Initializes Reddit object from 'praw.ini' credentials file """

        self.__reddit = praw.Reddit('supplementary-reddit-data')


    def get_user_created_utc(self, username: str) -> int:
        """
        Get user's 'created_utc' from username

        From a Reddit user's username, get the (POSIX) timestamp of when the
        Reddit user's account was created

        :param username: (string) Reddit user's username
        :return: (int) POSIX timestamp (number of seconds since the Unix epoch)
        of when Reddit user's account was created
        """

        try:
            user = self.__reddit.redditor(username)
            return user.created_utc

        except prawcore.exceptions.NotFound:
            raise UserNotFoundException(Exception)

        except AttributeError:
            raise NoCreatedUTCException(Exception)

