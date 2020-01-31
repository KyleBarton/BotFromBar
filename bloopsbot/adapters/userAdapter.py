import requests
import slack
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class UserAdapter:
    def __init__(self, slackClient):
        #self.teamId = teamId
        self.client = slackClient

    def getUserById(self, userId):
        try:
            return self.client.users_info(user=userId)
        except:
            logger.error("Could not get user info")
            raise
