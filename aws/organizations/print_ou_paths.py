# Prints a list of all OU paths. To be run from the Organization management account.

# Usage:
# pip install boto3
# python print_ou_paths.py

import boto3

client = boto3.client('organizations')

def list_all_organizational_units(parent_id, path):
    response = client.list_organizational_units_for_parent(ParentId=parent_id) 
    ous = response['OrganizationalUnits']
    for ou in ous:
        ou_path = f"{path + ' / ' if path else ''}{ou['Name']}"
        print(ou_path)
        list_all_organizational_units(ou['Id'], ou_path)

def main():
    roots = client.list_roots()
    root_id = roots['Roots'][0]['Id']
    list_all_organizational_units(root_id, "")

if __name__ == "__main__":
    main()
