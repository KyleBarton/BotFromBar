from models.slackevent import SlackEvent
def isPointsMessage(slackEvent: SlackEvent):
    return "++" in slackEvent.fullMessage or "--" in slackEvent.fullMessage


def processPointsMessage(slackEvent: SlackEvent, pointsRepository):
    msg = slackEvent.fullMessage
    plusSplit = [x.strip() for x in msg.split("++")]
    #let's not process if this isn't a simple plusplus for now
    if len(plusSplit) == 2:
        subject = cleanseSubject(plusSplit[0])
        reason = cleanseReason(plusSplit[1])
        points = pointsRepository.processPlusMessage(subject, reason)
        pointNoun = 'point' if points == 1 else 'points'
        if reason:
            return f'{subject} has {points} {pointNoun}, most recently for {reason}'
        else:
            return f'{subject} has {points} {pointNoun}'

    minusSplit = [x.strip() for x in msg.split("--")]
    if len(minusSplit) == 2:
        subject = cleanseSubject(minusSplit[0])
        reason = cleanseReason(minusSplit[1])
        points = pointsRepository.processMinusMessage(subject, reason)
        pointNoun = 'point' if points == 1 else 'points'
        if reason:
            return f'{subject} is down to {points} {pointNoun}, most recently for {reason}'
        else:
            return f'{subject} is down to {points} {pointNoun}'




## Private methods I guess
def cleanseSubject(subject):
    return (subject
        .strip("<>")
        .strip("@ ")
        .replace("++", "")
        .replace("--","").lower()
    )

def cleanseReason(reason):
    cleansedReason = reason
    if reason[:3] == "for":
        cleansedReason = reason[3:]
    return cleansedReason.strip().replace("++", "").replace("--","")