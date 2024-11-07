# Generates a CSV containing the Alternate Contacts for all accounts within an AWS Organization.
# To be run from the Organization management account.

# Usage:
# pip install boto3 botocove
# python get_iam_credential_report.py

from botocove import cove
import csv

CONTACT_TYPES = ['BILLING', 'OPERATIONS', 'SECURITY']
CONTACT_FIELDS = ['Name', 'EmailAddress', 'PhoneNumber', 'Title']

@cove(
#        target_ids=[],
#        ignore_ids=[]
)
def get_alternate_contact_rows(session):
    row = []
    account_client = session.client("account")
    for type in CONTACT_TYPES:
        try:
            contact = account_client.get_alternate_contact(AlternateContactType=type).get('AlternateContact')
            for field in CONTACT_FIELDS:
                row.append( contact.get(field) )
        except:
            row += [None for i in CONTACT_FIELDS]
    return row

def main():
    rows = [ ['Account', 'RootEmailAddress'] + [f'{t}_{f}' for t in CONTACT_TYPES for f in CONTACT_FIELDS] ]
    result = get_alternate_contact_rows()['Results']
    for r in result:
        rows.append([r['Id'], r['Email'] ] + r['Result'])
    with open('account_alternate_contacts.csv', 'w') as fout:
        w = csv.writer(fout)
        w.writerows(rows)

if __name__ == '__main__':
    main()