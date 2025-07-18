# Replays the CloudTrail events to SNS for when a new log object is written.

# Usage:
# pip install boto3
# python replay-cloudtrail-s3-events.py <CLOUDTRAIL_BUCKET_NAME> <DATE> <SNS_TOPIC_ARN>

import boto3
import json
import sys

account = boto3.client("account")
organizations = boto3.client('organizations')
s3 = boto3.client('s3')
sns = boto3.client('sns')

CLOUDTRAIL_BUCKET_NAME = sys.argv[1]
DATE = sys.argv[2] # Expected format: YYYY/MM/DD
SNS_TOPIC_ARN = sys.argv[3]

def get_full_result(client, method, args):
    p = client.get_paginator(method)
    return p.paginate(**args).build_full_result()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python replay-cloudtrail-s3-events.py <CLOUDTRAIL_BUCKET_NAME> <DATE> <SNS_TOPIC_ARN>")
        sys.exit(1)
    org = organizations.describe_organization()['Organization']
    org_id = org['Id']
    org_management_account_id = org['MasterAccountId']
    accounts = [i.get("Id") for i in get_full_result(organizations, 'list_accounts', {})["Accounts"]]
    regions = [i.get("RegionName") for i in get_full_result(account, 'list_regions', {})['Regions']]
    for accountId in accounts:
        for region in regions:
            prefix = f"AWSLogs/{org_id}/{accountId}/CloudTrail/{region}/{DATE}/"
            print(f"Listing objects for prefix {prefix}")
            log_objects = get_full_result(s3, 'list_objects_v2', {'Bucket': CLOUDTRAIL_BUCKET_NAME, 'Prefix': prefix}).get('Contents', [])
            chunks = [log_objects[i:i + 10] for i in range(0, len(log_objects), 10)]
            for chunk in chunks:
                messages = [{"s3Bucket": CLOUDTRAIL_BUCKET_NAME, "s3ObjectKey": [i['Key']]} for i in chunk]
                sns.publish_batch(
                    TopicArn=SNS_TOPIC_ARN,
                    PublishBatchRequestEntries=[
                        {
                            'Id': str(i),
                            'Message': json.dumps(message)
                        } for i, message in enumerate(messages)
                    ]
                )
            print(f"Published {len(log_objects)} messages to SNS topic {SNS_TOPIC_ARN} for account {accountId} in region {region}.")
