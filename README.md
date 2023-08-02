# AKS example

This assumes you've already got python, pip and Pulumi installed.

To run this:

1. Clone this repo: `git clone https://github.com/pierskarsenbarg/aks-get-managed-cluster`
1. Change directory: `cd aks-get-managed-cluster`
1. Add stack: `pulumi stack init {stackname}`
1. Add Azure location: `pulumi config set azure-native:location {location}`
1. Add subscription id: `pulumi config set subscriptionid {subscriptionid}`
1. Add virtual network cidr: `pulumi config set vnetcidr {vnetcidr}`
1. Add subnet cidr: `pulumi config set subnetcidr {subnetcidr}`
1. Add virtual environment: `python3 -m venv venv`
1. Activate virtual environment: `source venv/bin/activate`
1. Install requirements: `pip3 install -r requirements.txt`
1. Deploy: `pulumi up`