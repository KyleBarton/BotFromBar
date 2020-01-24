from models.slackevent import SlackEvent

def isBotMention(slackEvent: SlackEvent):
    return slackEvent.type == "app_mention"

def processBotMention(slackEvent: SlackEvent):
    return "You talking to me?"