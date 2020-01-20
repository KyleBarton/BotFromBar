from models.slackevent import SlackEvent
def isPointsMessage(slackEvent: SlackEvent):
    return "++" in slackEvent.fullMessage or "--" in slackEvent.fullMessage


def processPointsMessage(slackEvent: SlackEvent):
    msg = slackEvent.fullMessage
    plusSplit = [x.strip() for x in msg.split("++")]
    #let's not process if this isn't a simple plusplus for now
    if len(plusSplit) == 2:
        #todo hook up state
        subject = cleanseSubject(plusSplit[0])
        reason = cleanseReason(plusSplit[1])
        return f'{subject} has 1 point, most recently for {reason}'

    minusSplit = [x.strip() for x in msg.split("--")]
    if len(minusSplit) == 2:
        #todo hook up state
        subject = cleanseSubject(minusSplit[0])
        reason = cleanseReason(minusSplit[1])
        return f'{subject} is down to 1 point, most recently for {reason}'




## Private methods I guess
def cleanseSubject(subject):
    return subject.strip("@ ")

def cleanseReason(reason):
    cleansedReason = reason
    if reason[:3] == "for":
        cleansedReason = reason[3:]
    return cleansedReason.strip()