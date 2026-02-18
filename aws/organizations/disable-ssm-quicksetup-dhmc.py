# Undoes the damage caused by the SSM Automations run by the AWS-QuickSetup-DHMC-TA StackSet.
# To be run from the Organization management account after the StackSet has been deleted.

# Usage:
# pip install boto3 botocove
# python disable-ssm-quicksetup-dhmc.py

import boto3
from botocove import cove

SERVICE_SETTINGS = [
    "/ssm/managed-instance/default-ec2-instance-management-role",
    "/ssm/opsitem/ssm-patchmanager",
    "/ssm/opsitem/EC2",
    "/ssm/opsdata/ConfigCompliance",
    "/ssm/opsdata/Association",
    "/ssm/opsdata/OpsData-TrustedAdvisor",
    "/ssm/opsdata/ComputeOptimizer",
    "/ssm/opsdata/SupportCenterCase",
    "/ssm/opsdata/ExplorerOnboarded",
]


@cove(
    # target_ids=[],
    # ignore_ids=[],
    regions=[r["RegionName"] for r in boto3.client("ec2").describe_regions()["Regions"]],
)
def disable_ssm_dhmc(session):
    iam = session.client("iam")
    ssm = session.client("ssm")
    region = session.region_name
    role_name = f"AWS-QuickSetup-SSM-DefaultEC2MgmtRole-{region}"
    for s in SERVICE_SETTINGS:
        ssm.reset_service_setting(
            SettingId=s
        )
    iam.detach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedEC2InstanceDefaultPolicy",
    )
    iam.delete_role(RoleName=role_name)

if __name__ == '__main__':
    disable_ssm_dhmc()
