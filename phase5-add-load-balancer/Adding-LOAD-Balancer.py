import boto3
import time

# Initialize boto3 clients
elb_client = boto3.client('elbv2', region_name='ap-south-1')
ec2_client = boto3.client('ec2', region_name='ap-south-1')
ec2_resource = boto3.resource('ec2', region_name='ap-south-1')

def create_subnet_in_different_az(vpc_id, existing_subnet_az, cidr_block='172.31.80.0/20'):
    """Create a new subnet in a different AZ than the existing subnet"""
    # Get available AZs in the region
    available_azs = ec2_client.describe_availability_zones()['AvailabilityZones']
    
    # Find an AZ different from the existing subnet's AZ
    target_az = None
    for az in available_azs:
        if az['ZoneName'] != existing_subnet_az and az['State'] == 'available':
            target_az = az['ZoneName']
            break
    
    if not target_az:
        print("Could not find an available AZ different from the existing subnet")
        return None
    
    print(f"Creating new subnet in {target_az}")
    
    # Create the subnet
    subnet = ec2_client.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cidr_block,
        AvailabilityZone=target_az,
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': f'LB-Subnet-{target_az}'
                    }
                ]
            }
        ]
    )
    
    subnet_id = subnet['Subnet']['SubnetId']
    print(f"Created subnet {subnet_id} in {target_az}")
    
    # Modify subnet to auto-assign public IPs
    ec2_client.modify_subnet_attribute(
        SubnetId=subnet_id,
        MapPublicIpOnLaunch={'Value': True}
    )
    
    return subnet_id

def get_subnet_az(subnet_id):
    """Get the availability zone of a subnet"""
    subnet = ec2_client.describe_subnets(SubnetIds=[subnet_id])['Subnets'][0]
    return subnet['AvailabilityZone']

def create_load_balancer_with_instances(frontend_ips, vpc_id, subnet_ids, security_group_id):
    # Step 1: Get the instance IDs from the IP addresses
    instance_ids = []
    for ip in frontend_ips:
        # Get instances with the specific public IP
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'ip-address',
                    'Values': [ip]
                }
            ]
        )
        
        # Extract instance IDs
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])
                print(f"Found instance {instance['InstanceId']} with IP {ip}")
    
    if not instance_ids:
        print("No instances found with the provided IPs!")
        return None, None
    
    # Step 2: Create a target group
    target_group_name = 'FrontendTargetGroup'
    target_group_response = elb_client.create_target_group(
        Name=target_group_name,
        Protocol='HTTP',
        Port=80,  # Assuming your frontend app runs on port 80
        VpcId=vpc_id,
        HealthCheckProtocol='HTTP',
        HealthCheckPort='80',
        HealthCheckPath='/',  # Adjust to a path that returns 200 OK for your app
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=5,
        UnhealthyThresholdCount=2,
        Matcher={
            'HttpCode': '200-399'  # HTTP status codes for healthy targets
        },
        TargetType='instance'
    )
    
    target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']
    print(f"Created target group: {target_group_name} with ARN: {target_group_arn}")
    
    # Step 3: Register instances with the target group
    elb_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance_id} for instance_id in instance_ids]
    )
    print(f"Registered instances {instance_ids} with target group")
    
    # Step 4: Create the load balancer
    lb_name = 'FrontendLoadBalancer'
    load_balancer_response = elb_client.create_load_balancer(
        Name=lb_name,
        Subnets=subnet_ids,  # Need at least 2 subnets in different AZs
        SecurityGroups=[security_group_id],
        Scheme='internet-facing',
        Tags=[
            {
                'Key': 'Name',
                'Value': 'TravelMemory-Frontend-LB'
            }
        ],
        Type='application',
        IpAddressType='ipv4'
    )
    
    load_balancer_arn = load_balancer_response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"Created load balancer: {lb_name} with ARN: {load_balancer_arn}")
    
    # Wait for the load balancer to be available
    print("Waiting for load balancer to be available...")
    waiter = elb_client.get_waiter('load_balancer_available')
    waiter.wait(LoadBalancerArns=[load_balancer_arn])
    
    # Step 5: Create a listener to forward traffic to the target group
    listener_response = elb_client.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn
            }
        ]
    )
    
    print(f"Created listener for load balancer")
    
    # Get the DNS name of the load balancer
    lb_info = elb_client.describe_load_balancers(LoadBalancerArns=[load_balancer_arn])
    dns_name = lb_info['LoadBalancers'][0]['DNSName']
    
    print(f"\nLoad balancer setup complete!")
    print(f"Load Balancer DNS: {dns_name}")
    print(f"Target Group ARN: {target_group_arn}")
    
    return load_balancer_arn, target_group_arn

def main():
    # Your frontend instances public IPs
    frontend_ips = ['13.126.0.158', '3.109.71.149']
    
    # Your VPC information
    vpc_id = 'vpc-0056d809452f9f8ea'  # From your previous images
    
    # Your existing subnet
    existing_subnet_id = 'subnet-0c1842aca7dc1b6b0'  # From your previous images (ap-south-1b)
    
    # Get the AZ of your existing subnet
    existing_subnet_az = get_subnet_az(existing_subnet_id)
    print(f"Existing subnet is in {existing_subnet_az}")
    
    # Create a new subnet in a different AZ
    new_subnet_id = create_subnet_in_different_az(vpc_id, existing_subnet_az)
    if not new_subnet_id:
        print("Failed to create a new subnet. Cannot proceed with load balancer creation.")
        return
    
    # Subnet IDs for the load balancer (need at least 2 in different AZs)
    subnet_ids = [existing_subnet_id, new_subnet_id]
    
    # Security group that allows HTTP traffic (port 80)
    security_group_id = 'sg-036f8d6933b57505b'  # TravelMemorySG-Prince
    
    # Create load balancer and target group
    lb_arn, tg_arn = create_load_balancer_with_instances(
        frontend_ips,
        vpc_id,
        subnet_ids,
        security_group_id
    )

if __name__ == "__main__":
    main()