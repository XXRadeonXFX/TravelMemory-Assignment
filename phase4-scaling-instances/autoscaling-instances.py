import boto3

# Initialize boto3 clients
ec2_client = boto3.client('ec2', region_name='ap-south-1')
ec2_resource = boto3.resource('ec2', region_name='ap-south-1')

# Function to create an AMI from an instance
def create_ami(instance_id, name):
    response = ec2_client.create_image(
        InstanceId=instance_id,
        Name=name,
        Description=f'AMI for {name}',
        NoReboot=True  # Set to False if you want to reboot during AMI creation
    )
    ami_id = response['ImageId']
    print(f"Creating AMI {ami_id} for {name}...")
    
    # Wait for AMI to be available
    waiter = ec2_client.get_waiter('image_available')
    waiter.wait(ImageIds=[ami_id])
    print(f"AMI {ami_id} for {name} is now available")
    
    return ami_id

# Function to launch an instance from AMI and assign Elastic IP with custom name
def launch_instance_with_eip(ami_id, instance_type, subnet_id, security_group_id, instance_name, eip_name):
    # Launch instance
    instance = ec2_resource.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        SubnetId=subnet_id,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name
                    }
                ]
            }
        ]
    )[0]
    
    print(f"Launching instance {instance.id} from AMI {ami_id}...")
    
    # Wait for instance to be running
    instance.wait_until_running()
    print(f"Instance {instance.id} is now running")
    
    # Allocate Elastic IP
    allocation_response = ec2_client.allocate_address(Domain='vpc')
    elastic_ip = allocation_response['PublicIp']
    allocation_id = allocation_response['AllocationId']
    
    # Tag the Elastic IP with custom name
    ec2_client.create_tags(
        Resources=[allocation_id],
        Tags=[
            {
                'Key': 'Name',
                'Value': eip_name
            }
        ]
    )
    
    # Associate Elastic IP with the instance
    ec2_client.associate_address(
        AllocationId=allocation_id,
        InstanceId=instance.id
    )
    
    print(f"Elastic IP {elastic_ip} named '{eip_name}' allocated and associated with instance {instance.id}")
    
    return instance.id, elastic_ip

# Main execution
def main():
    # IDs from your images - using the actual values from your screenshots
    frontend_instance_id = 'i-0e9c849f2c1c016d6'  # TM-Prince-Frontend
    backend_instance_id = 'i-093078ec28ca53fc7'  # TM-Prince-Backend
    
    # Your VPC subnet and security group - from your screenshots
    subnet_id = 'subnet-0c1842aca7dc1b6b0'  # ap-south-1b subnet
    security_group_id = 'sg-036f8d6933b57505b'  # TravelMemorySG-Prince
    
    # Create AMIs
    frontend_ami_id = create_ami(frontend_instance_id, 'TM-Prince-Frontend-AMI')
    backend_ami_id = create_ami(backend_instance_id, 'TM-Prince-Backend-AMI')
    
    # Launch new instances from AMIs with Elastic IPs and custom names
    new_frontend_id, frontend_eip = launch_instance_with_eip(
        frontend_ami_id, 
        't2.micro', 
        subnet_id, 
        security_group_id, 
        'TM-Prince-Frontend-Copy',
        'FrontendEIP-Copy1'
    )
    
    new_backend_id, backend_eip = launch_instance_with_eip(
        backend_ami_id, 
        't2.micro', 
        subnet_id, 
        security_group_id, 
        'TM-Prince-Backend-Copy',
        'BackendEIP-Copy1'
    )
    
    print("\nSummary:")
    print(f"New Frontend Instance: {new_frontend_id} with Elastic IP: {frontend_eip} (FrontendEIP-Copy1)")
    print(f"New Backend Instance: {new_backend_id} with Elastic IP: {backend_eip} (BackendEIP-Copy1)")

if __name__ == "__main__":
    main()