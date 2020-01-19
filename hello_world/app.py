import json

import requests
import os
import slack

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handleMention(requestBody):
    #ape the message
    #UGGGH there has to be an sdk that could deserialize this
    rich_text = [
        rt for rt in requestBody["event"]["blocks"]
        if rt["type"] == "rich_text"
    ][0]
    text = [
        obj for obj in
        rich_text["elements"][0]["elements"]
        if obj["type"] == "text"
    ][0]["text"]
    return text
    

def lambda_handler(event, context):
    ZK_API_TOKEN = os.getenv("TOKEN")
    if not event["body"]:
        return {
            "statusCode": 400,
            "body": "Need a body"
        }
    
    requestBody = json.loads(event["body"])
    logger.info("request:")
    logger.info(requestBody)
    #Handle a challenge if slack needs integrating
    if "challenge" in requestBody:
        return {
            "statusCode": 200,
            "body": requestBody["challenge"]
        }
    response = None
    if "event" in requestBody and "type" in requestBody["event"]:
        if (requestBody["event"]["type"] == "app_mention"):
            response = handleMention(requestBody)
    
    if response:
        logger.info(response)
        client = slack.WebClient(token=ZK_API_TOKEN)
        response = client.chat_postMessage(
            channel='#bottesting',
            text=json.dumps(response)
        )

    return {
        "statusCode": 200,
        "body": "App mention handled"
    }
