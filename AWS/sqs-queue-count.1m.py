#!/usr/bin/env python3
import sys

try:
    import boto3

    has_boto3 = True
except ImportError:
    has_boto3 = False

from collections import namedtuple

Queue = namedtuple('Queue', 'name depth inflight')


def get_queue_attributes(client, queue_url):
    response = client.get_queue_attributes(QueueUrl=queue_url,
                                           AttributeNames=['ApproximateNumberOfMessages',
                                                           'ApproximateNumberOfMessagesNotVisible',
                                                           'QueueArn'])
    depth = response['Attributes']['ApproximateNumberOfMessages']
    inflight = response['Attributes']['ApproximateNumberOfMessagesNotVisible']
    arn = response['Attributes']['QueueArn']
    name = arn.split(':')[-1]

    return Queue(name=name, depth=int(depth), inflight=int(inflight))


if __name__ == '__main__':
    print('SQS')
    if not has_boto3:
        print('`pip install boto3` first')
        sys.exit(0)

    print('---')

    client = boto3.client('sqs')
    queue_urls = client.list_queues()['QueueUrls']
    queues = [get_queue_attributes(client, queue_url) for queue_url in queue_urls]
    queues.sort(key=lambda x: x.depth, reverse=True)

    for queue in queues:
        if queue.depth == 0:
            continue

        print(queue.name, '| color=blue')
        print('Depth: {} — In-flight: {} | size=11'.format(queue.depth, queue.inflight))
