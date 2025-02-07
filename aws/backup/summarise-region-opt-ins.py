# Generates 2 CSVs summarising the opted-in resource types for AWS Backup for each region.

# Usage:
# pip install boto3
# python summarise-region-opt-ins.py

import boto3
import csv


def dict_to_table(data):
    services = set()
    for region in data:
        services.update(data[region].keys())
    services = sorted(services)
    header = ["Region"] + services
    rows = []
    for region, services_dict in data.items():
        row = [region]
        for service in services:
            row.append(services_dict.get(service, ""))
        rows.append(row)
    table = [header] + rows
    return table


home_client = boto3.client('ec2')
regions = home_client.describe_regions()['Regions']
opt_in, managed = {}, {}
for region in regions:
    region_name = region['RegionName']
    backup = boto3.client('backup', region_name=region_name)
    region_settings = backup.describe_region_settings()
    opt_in[region_name]= region_settings['ResourceTypeOptInPreference']
    managed[region_name] = region_settings['ResourceTypeManagementPreference']
with open('opt_in.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(dict_to_table(opt_in))
with open('managed.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(dict_to_table(managed))
