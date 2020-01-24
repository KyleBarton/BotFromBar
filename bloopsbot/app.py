import json

import requests
import os
import slack

import logging
from pointsHandler import isPointsMessage
from pointsHandler import processPointsMessage
from botMentionHandler import isBotMention
from botMentionHandler import processBotMention
from models.slackevent import SlackEvent
from data.pointsRepository import PointsRepository
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ZK_API_TOKEN = os.getenv("TOKEN")

# def handleMention_sass(slackEvent: SlackEvent):
#     return "you talking to me?"
    
def parseLambdaEvent(event):
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

def handleEvent(slackEvent: SlackEvent):
    pointsRepository = PointsRepository("BloopsPoints", slackEvent.teamId) #todo read from environ
    #It's important that bot not handle its own points, because it will count twice.
    if isBotMention(slackEvent):
        return processBotMention(slackEvent)
    if isPointsMessage(slackEvent):
        return processPointsMessage(slackEvent, pointsRepository)
    logger.info('slack event not handled:')
    logger.info(slackEvent.raw)
    return None


def lambda_handler_safe(event, context):
    logger.info("request:")
    requestBody = parseLambdaEvent(event)
    if not requestBody:
        logger.error("bad request:\n " + str(event))
        return {
            "statusCode": 400,
            "body": "request was malformed, check logs"
        }
    logger.info(requestBody)
    #Handle a challenge if slack needs integrating
    if "challenge" in requestBody:
        return {
            "statusCode": 200,
            "body": requestBody["challenge"]
        }

    slackEvent = SlackEvent(requestBody)
    response = handleEvent(slackEvent)
    
    if response:
        logger.info(response)
        logger.info('Would normally post in channel: ' + slackEvent.channelId)
        client = slack.WebClient(token=ZK_API_TOKEN)
        response = client.chat_postMessage(
            channel='#bot-talk',
            text=json.dumps(response)
        )

        return {
            "statusCode": 200,
            "body": "App mention handled"
        }

    return {
        "statusCode": 200,
        "body": "Check logs for message"
    }

def lambda_handler_emergency(event, context):
    return {
        "statusCode": 200,
        "body": "Check logs for message"
    }


def lambda_handler(event, context):
    # return lambda_handler_emergency(event, context)
    return lambda_handler_safe(event, context)