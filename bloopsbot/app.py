import json

import requests
import os
import slack

import logging
from pointsHandler import isPointsMessage
from pointsHandler import processPointsMessage
from models.slackevent import SlackEvent
from data.pointsRepository import PointsRepository
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ZK_API_TOKEN = os.getenv("TOKEN")

def handleMention_sass(slackEvent: SlackEvent):
    return "you talking to me?"
def handleMention_ape(slackEvent: SlackEvent):
    #ape the message
    #TODO don't use raw, just parse this in slackEvent
    rich_text = [
        rt for rt in slackEvent.raw["event"]["blocks"]
        if rt["type"] == "rich_text"
    ][0]
    text = [
        obj for obj in
        rich_text["elements"][0]["elements"]
        if obj["type"] == "text"
    ][0]["text"]
    return text
    
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

def handleMessage(slackEvent: SlackEvent):
    logger.info("message event")
    logger.info(slackEvent.raw["event"])
    pointsRepository = PointsRepository("BloopsPoints") #todo read from environ
    if isPointsMessage(slackEvent):
        return processPointsMessage(slackEvent, pointsRepository)
    return None

def lambda_handler(event, context):
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
    response = None
    slackEvent = SlackEvent(requestBody)
    if slackEvent.type == "message":
        response = handleMessage(slackEvent)
    if slackEvent.type == "app_mention":
        response = handleMention_sass(slackEvent)
    
    # if "event" in requestBody and "type" in requestBody["event"]:
    #     if (requestBody["event"]["type"] == "app_mention"):
    #         response = handleMention_sass(requestBody)
    #     if (requestBody["event"]["type"] == "message"):
    #         logger.info("message event")
    #         logger.info(requestBody["event"])
    
    if response:
        logger.info(response)
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
