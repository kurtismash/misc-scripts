# Generates a CSV containing the support plan for all member accounts within an AWS Organization.
# To be run from the Organization management account.

# Usage:
# pip install boto3 botocove
# python get_account_support_plans.py

import botocore.exceptions
import csv
from botocove import cove


@cove(
    # target_ids=[],
    # ignore_ids=[],
    regions=["us-east-1"],
)
def get_support_plan(session):
    support_client = session.client("support")
    try:
        severity_levels = support_client.describe_severity_levels(language="en")
        levels = severity_levels.get("severityLevels", [])
        level_codes = {level["code"] for level in levels}
        if "critical" in level_codes:
            return "Business/Enterprise"
        return "Basic"
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "SubscriptionRequiredException":
            # This means the account has Basic support (no paid plan)
            return "Basic"
        raise e


def main():
    rows = [["AccountNumber", "AccountName", "RootEmailAddress", "SupportPlan"]]
    result = get_support_plan()
    if result["Exceptions"]:
        for r in result["Exceptions"]:
            print(r)
    for r in result["Results"]:
        rows.append([r["Id"], r["Name"], r["Email"], r["Result"]])
    with open("account_support_plans.csv", "w") as fout:
        w = csv.writer(fout)
        w.writerows(rows)


if __name__ == "__main__":
    main()
