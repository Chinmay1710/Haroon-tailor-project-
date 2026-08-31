#!/bin/bash

# Install aws cli v2
echo "# Installing the V2 AWs CLI."
sudo rm -rf /usr/local/aws && sudo rm /usr/local/bin/aws
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Install boto3
echo "# Installing the python Boto3 library."
sudo pip3 install boto3

# Install the node modules for the node server
echo "# Installing node modules for the node server"
cd /home/ec2-user/environment/node_server
npm install

# Run the python setup script to deploy CloudFront & update the ec2 secuity group
echo "# Setting up the EC2 Security Group and CloudFront."
cd /home/ec2-user/environment/resources
python3 setup.py

# Getting CloudFront domain
echo "# The S3 bucket name is: "
aws s3api list-buckets --query Buckets[0].Name
echo "# The CloudFront distribution domain is: "
aws cloudfront list-distributions --query DistributionList.Items[0].DomainName
