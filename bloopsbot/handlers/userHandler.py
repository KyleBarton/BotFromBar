import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
#kiss
def getUserNameById(userId, userAdapter):
    userId = userId.strip("<@>")
    response = userAdapter.getUserById(userId)
    logger.info("user lookup response:")
    logger.info(response)
    return response["user"]["name"]