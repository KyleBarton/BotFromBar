import json

import requests
import os
import re
import slack

import logging
from handlers.pointsHandler import isPointsMessage
from handlers.pointsHandler import processPointsMessage
from handlers.userHandler import getUserNameById
from botMentionHandler import isBotMention
from botMentionHandler import processBotMention
from models.slackevent import SlackEvent
from data.pointsRepository import PointsRepository
from adapters.userAdapter import UserAdapter
from adapters.slackClientFactory import getSlackClient
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parseLambdaEvent(event):
    logger.info("Event: ")
    logger.info(event)
    if "headers" in event and "X-Slack-Retry-Num" in event["headers"]:
        #We've taken too long to respond or errored on a request. Respond quickly to prevent more retries
        # long term, we should de-dupe requests more robustly, and put a queue between event handling and processing
        return None
    if "body" not in event:
        return None
    rawRequest = event["body"]
    if not event["body"]:
        logger.error("Bad json sent in event: no body.\n event: {}", event)
        return None
    try:
        return json.loads(rawRequest)
    except ValueError as e:
        logger.error("Bad json sent in event.\nBody: {}\nError: {}", rawRequest, e)
        return None

def cleanMessage(text, userAdapter):
    mentions = re.findall("<@.*?>", text)
    for mention in mentions:
        name = getUserNameById(mention, userAdapter)
        text = text.replace(mention, name)
    channelMentions = re.findall("<#.*?>", text)
    for channelMention in channelMentions:
        text = text.replace(channelMention, channelMention.strip("<>").split("|")[1])
    return text

def handleEvent(slackEvent: SlackEvent, userAdapter: UserAdapter):
    pointsRepository = PointsRepository("BloopsPoints", slackEvent.teamId) #todo read from environ
    #It's important that bot not handle its own points, because it will count twice.
    if isBotMention(slackEvent):
        return processBotMention(slackEvent)
    if isPointsMessage(slackEvent):
        #antipattern here needs work
        slackEvent.fullMessage = cleanMessage(slackEvent.fullMessage, userAdapter)
        return processPointsMessage(slackEvent, pointsRepository)
    logger.info('slack event not handled:')
    logger.info(slackEvent.raw)
    return None

def lambda_handler_safe(event, context):
    slackApiToken = os.getenv("TOKEN")
    slackClient = getSlackClient(slackApiToken)
    userAdapter = UserAdapter(slackClient)
    requestBody = parseLambdaEvent(event)
    if not requestBody:
        logger.error("Request not parseable by bloopsbot:\n " + str(event))
        #respond 200 to slack, since its on this app to figure out how to parse it
        return {
            "statusCode": 200,
            "body": "ok"
        }
    logger.info(requestBody)
    #Handle a challenge if slack needs integrating
    if "challenge" in requestBody:
        return {
            "statusCode": 200,
            "body": requestBody["challenge"]
        }

    slackEvent = SlackEvent(requestBody)
    response = handleEvent(slackEvent, userAdapter)
    
    if response:
        logger.info(response)
        client = slackClient
        slackClientResponse = client.chat_postMessage(
            channel=slackEvent.channelId,
            text=json.dumps(response)
        )

        return {
            "statusCode": 200,
            "body": {
                "MessageHandled": True,
                "ResponseMessage": json.dumps(response)
            }
        }

    return {
        "statusCode": 200,
        "body": {
            "MessageHandled": False,
        }
    }

def lambda_handler(event, context):
    return lambda_handler_safe(event, context)