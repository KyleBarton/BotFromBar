import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
CHANNEL = "channel"

class SlackEvent:
    def __init__(self, eventJson):
        #access json when experimenting, turn into a property when access is understood
        self.raw = eventJson
        try:
            event = self.raw["event"]
            self.teamId = self.raw["team_id"]
            self.type = event["type"]
            self.fullMessage = event["text"]
            # if self.raw["event"]["channel_type"] == CHANNEL:
            if CHANNEL in event:
                self.channelId = event["channel"]
        except:
            logger.error("Couldn't initiate slack event")
            raise