import boto3
from boto3.dynamodb.conditions import Key #, Attr not needed
import json
import time

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Get the service resource.

# Instantiate a table resource object without actually
# creating a DynamoDB table. Note that the attributes of this table
# are lazy-loaded: a request is not made nor are the attribute
# values populated until the attributes
# on the table resource are accessed or its load() method is called.

class PointsRepository:
    def __init__(self, tableName, teamId):
        self.tableName = tableName
        self.teamId = teamId
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(tableName)

    def processPlusMessage(self, subject, reason):
        return self.__processPointsMessage(subject, reason, 1)

    def processMinusMessage(self, subject, reason):
        return self.__processPointsMessage(subject, reason, -1)

    def __processPointsMessage(self, subject, reason, pointIncr):
        queryResponse = self.table.query(
            KeyConditionExpression=Key('subject').eq(subject)
        )
        logger.info('query:')
        logger.info(queryResponse)
        if not reason:
            reason = 'NONE'
        if len(queryResponse['Items']) == 0:
            newPoints = pointIncr
            self.table.put_item(
                Item={
                    'subject': subject,
                    'teamId': self.teamId,
                    'points': newPoints,
                    'reasons': [
                        {
                            'reason': reason,
                            'time': int(time.time()),
                            'sentiment': pointIncr # -1 for a minus reason, +1 for a plus reason
                        }
                    ]
                }
            )
            return newPoints
        else:
            currentPointsResponse = queryResponse['Items'][0]
            currentPoints = currentPointsResponse['points']
            newPoints = currentPoints + pointIncr
            newReason = {
                'reason': reason,
                'time': int(time.time()),
                'sentiment': pointIncr
            }
            self.table.update_item(
                Key={
                    'subject': subject,
                    'teamId': self.teamId
                },
                UpdateExpression='SET points = :pts, reasons = list_append(reasons, :rsn)',
                ExpressionAttributeValues={
                    ':pts': newPoints,
                    ':rsn': [newReason]
                }
            )
            return newPoints