import json
            # channel=slackEvent.channelId,
            # text=json.dumps(response)
class MockSlackClient:
    def __init__(self, token):
        self.token = token
    def chat_postMessage(self, **kwargs):
        if "channel" not in kwargs:
            raise "Must specify channel"
        if "text" not in kwargs:
            raise "Must specify text"
        try:
            json.loads(kwargs["text"])
        except:
            raise "Text must be json"