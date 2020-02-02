import slack
import os
import logging
from local.mockSlackClient import MockSlackClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getSlackClient(authToken):
    logger.info("Stage:")
    logger.info(os.getenv("STAGE"))
    if os.getenv("STAGE") == "local":
        return MockSlackClient(authToken)
    return slack.WebClient(token=authToken)