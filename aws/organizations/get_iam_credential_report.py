# Generates an IAM Credential Report for each account within an AWS Organization and combines.
# To be run from the Organization management account. Will only update once every 4 hours due to limitations of IAM Credential Reports.

# Usage:
# pip install boto3 botocove
# python get_iam_credential_report.py

from botocove import cove


@cove(
    #  target_ids=[],
    #  ignore_ids=[]
)
def get_credential_report(session):
    iam_client = session.client("iam")
    iam_client.generate_credential_report()
    return iam_client.get_credential_report()["Content"].decode("utf-8")


def main():
    results = get_credential_report()["Results"]
    report_header = results[0]["Result"].split("\n")[0]
    csv = f"account,root_email_address,{report_header}\n"
    for result in results:
        rows = result["Result"].split("\n")[1:]
        for row in rows:
            csv += f"{result['Id']},{result['Email']},{row}\n"
    print(csv)
    with open("iam_credential_report.csv", "w") as fout:
        fout.write(csv)


if __name__ == "__main__":
    main()
