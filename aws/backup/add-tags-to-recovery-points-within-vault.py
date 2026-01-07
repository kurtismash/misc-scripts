# Adds tags to all recovery points within a specified backup vault.
# As AWS Backup wraps multiple services, you may need to add support for your backup sources.

import boto3

VAULT_NAME = ""
TAGS_TO_ADD = {}

backup = boto3.client("backup")
rds = boto3.client("rds")

paginator = backup.get_paginator("list_recovery_points_by_backup_vault")
for page in paginator.paginate(BackupVaultName=VAULT_NAME):
    for recovery_point in page["RecoveryPoints"]:
        print(recovery_point)
        arn = recovery_point["RecoveryPointArn"]
        owning_service = arn.split(":")[2]
        if owning_service == "backup":
            backup.tag_resource(ResourceArn=arn, Tags=TAGS_TO_ADD)
        elif owning_service == "rds":
            rds.add_tags_to_resource(
                ResourceName=arn,
                Tags=[{"Key": k, "Value": v} for k, v in TAGS_TO_ADD.items()],
            )
