class SlackEvent:
    def __init__(self, eventJson):
        #access json when experimenting, turn into a property when access is understood
        self.raw = eventJson
        try:
            self.type = self.raw["event"]["type"]
            self.fullMessage = self.raw["event"]["text"]
            # rich text parsing... maybe someday
            #if "subtype" not in self.raw["event"] or self.raw["event"]["subtype"] != "bot_message":
            #    self.messageParts = self.raw["event"]["blocks"][0]["elements"][0]["elements"]
        except:
            raise "Couldn't initiate slack event"