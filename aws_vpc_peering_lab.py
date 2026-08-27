import boto3
import time

def complete_vpc_peering_lab(
    region,
    requester_vpc_id, 
    accepter_vpc_id, 
    lab_public_rt_id, 
    shared_vpc_rt_id, 
    flow_log_role_arn
):
    ec2_client = boto3.client('ec2', region_name=region)
    logs_client = boto3.client('logs', region_name=region)

    print("Step 1: Creating VPC Peering Connection...")
    try:
        peering_response = ec2_client.create_vpc_peering_connection(
            VpcId=requester_vpc_id,
            PeerVpcId=accepter_vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc-peering-connection',
                    'Tags': [{'Key': 'Name', 'Value': 'Lab-Peer'}]
                }
            ]
        )
        peering_connection_id = peering_response['VpcPeeringConnection']['VpcPeeringConnectionId']
        print(f"Created Peering Connection: {peering_connection_id}")
    except Exception as e:
        print(f"Error creating peering connection: {e}")
        return
    
    # Wait a moment before accepting
    time.sleep(2)
    
    print("Step 2: Accepting VPC Peering Connection...")
    try:
        ec2_client.accept_vpc_peering_connection(
            VpcPeeringConnectionId=peering_connection_id
        )
        print("VPC Peering Connection Accepted.")
    except Exception as e:
        print(f"Error accepting peering connection: {e}")

    print("Step 3: Configuring Route Tables...")
    # Add route to Lab Public Route Table
    try:
        ec2_client.create_route(
            RouteTableId=lab_public_rt_id,
            DestinationCidrBlock='10.5.0.0/16',
            VpcPeeringConnectionId=peering_connection_id
        )
        print(f"Added route 10.5.0.0/16 -> {peering_connection_id} to {lab_public_rt_id}")
    except Exception as e:
        print(f"Error adding route to Lab RT: {e}")

    # Add route to Shared VPC Route Table
    try:
        ec2_client.create_route(
            RouteTableId=shared_vpc_rt_id,
            DestinationCidrBlock='10.0.0.0/16',
            VpcPeeringConnectionId=peering_connection_id
        )
        print(f"Added route 10.0.0.0/16 -> {peering_connection_id} to {shared_vpc_rt_id}")
    except Exception as e:
        print(f"Error adding route to Shared RT: {e}")

    print("Step 4: Enabling VPC Flow Logs for Shared VPC...")
    log_group_name = 'ShareVPCFlowLogs'
    try:
        logs_client.create_log_group(logGroupName=log_group_name)
        print(f"Created CloudWatch Log Group: {log_group_name}")
    except logs_client.exceptions.ResourceAlreadyExistsException:
        print(f"CloudWatch Log Group '{log_group_name}' already exists.")
    except Exception as e:
        print(f"Error creating Log Group: {e}")
        
    try:
        ec2_client.create_flow_logs(
            ResourceIds=[accepter_vpc_id],
            ResourceType='VPC',
            TrafficType='ALL',
            LogGroupName=log_group_name,
            DeliverLogsPermissionArn=flow_log_role_arn,
            MaxAggregationInterval=60
        )
        print("VPC Flow Logs enabled successfully.")
    except Exception as e:
        print(f"Error creating Flow Logs: {e}")
        
    print("\n--- Lab automation script complete! ---")
    print("Next step: Please proceed to Task 4 in your lab instructions to test the connection manually!")

if __name__ == "__main__":
    # =========================================================
    # YOUR ACTION REQUIRED: FILL IN YOUR LAB DETAILS BELOW
    # =========================================================
    
    AWS_REGION = 'us-east-1' # Ensure this matches your lab region!
    
    # Find these in the VPC Dashboard -> Your VPCs
    LAB_VPC_ID = 'vpc-xxxxxxxxxxxxxxxxx'
    SHARED_VPC_ID = 'vpc-yyyyyyyyyyyyyyyyy' 
    
    # Find these in the VPC Dashboard -> Route Tables
    LAB_PUBLIC_RT_ID = 'rtb-xxxxxxxxxxxxxxxxx' 
    SHARED_VPC_RT_ID = 'rtb-yyyyyyyyyyyyyyyyy' 
    
    # Find this in IAM -> Roles -> search 'vpc-flow-logs-Role'
    FLOW_LOG_ROLE_ARN = 'arn:aws:iam::123456789012:role/vpc-flow-logs-Role'
    
    # =========================================================

    complete_vpc_peering_lab(
        region=AWS_REGION,
        requester_vpc_id=LAB_VPC_ID,
        accepter_vpc_id=SHARED_VPC_ID,
        lab_public_rt_id=LAB_PUBLIC_RT_ID,
        shared_vpc_rt_id=SHARED_VPC_RT_ID,
        flow_log_role_arn=FLOW_LOG_ROLE_ARN
    )
