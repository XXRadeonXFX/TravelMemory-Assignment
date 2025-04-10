import boto3
import time
from botocore.exceptions import ClientError

# Initialize EC2 client - change region if needed
ec2 = boto3.client('ec2', region_name='ap-south-1')
sg_name = 'TravelMemorySG-Prince'

try:
    print("Creating security group...")
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description='Security group for my application'
    )
    sg_id = response['GroupId']
    print("Security group created:", sg_id)

    # Configure security group permissions
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 3000, 'ToPort': 3000, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    print("Inbound rules added.")
except ClientError as e:
    if 'InvalidGroup.Duplicate' in str(e):
        print("Security group already exists. Fetching its ID...")
        groups = ec2.describe_security_groups(GroupNames=[sg_name])
        sg_id = groups['SecurityGroups'][0]['GroupId']
        print("Security group ID:", sg_id)
    else:
        print(f"Error: {str(e)}")
        raise

print("Checking for existing EC2 instance...")
existing_instances = ec2.describe_instances(
    Filters=[
        {'Name': 'tag:Name', 'Values': ['TM-Prince-Backend']},
        {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
    ]
)

if existing_instances['Reservations']:
    instance = existing_instances['Reservations'][0]['Instances'][0]
    instance_id = instance['InstanceId']
    print(f"Reusing existing instance: {instance_id}")
else:
    print("Launching new EC2 instance...")
    # For us-east-1, this is Amazon Linux 2023
    # For other regions or OS, change the AMI ID
    instance = ec2.run_instances(
        ImageId='ami-0e35ddab05955cf57',  # Ubuntu in ap-south-1
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='TMKeyPrinceBackend',  # Replace with your key pair name
        SecurityGroupIds=[sg_id],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'TM-Prince-Backend'}]
        }]
    )['Instances'][0]
    instance_id = instance['InstanceId']
    print(f"New instance launched: {instance_id}")

    waiter = ec2.get_waiter('instance_running')
    print("Waiting for the instance to enter 'running' state...")
    waiter.wait(InstanceIds=[instance_id])
    print("Instance is now running.")

# --- Elastic IP allocation and association ---
try:
    print("Checking for tagged Elastic IPs...")
    addresses = ec2.describe_addresses()
    eip_allocation = None
    
    # First check for a tagged EIP with name "BackendEIP"
    for addr in addresses['Addresses']:
        if 'Tags' in addr:
            for tag in addr['Tags']:
                if tag['Key'] == 'Name' and tag['Value'] == 'BackendEIP':
                    eip_allocation = addr
                    break
        if eip_allocation:
            break

    # If no tagged EIP, check for any unassociated EIP
    if not eip_allocation:
        print("No tagged EIP found. Looking for any unassociated Elastic IP...")
        for addr in addresses['Addresses']:
            if 'InstanceId' not in addr:
                eip_allocation = addr
                # Tag this EIP for future use
                try:
                    ec2.create_tags(
                        Resources=[addr['AllocationId']], 
                        Tags=[{'Key': 'Name', 'Value': 'BackendEIP'}]
                    )
                    print(f"Tagged existing EIP {addr['PublicIp']} as BackendEIP")
                except Exception as e:
                    print(f"Warning: Could not tag EIP: {str(e)}")
                break

    # If we found an EIP to use
    if eip_allocation:
        allocation_id = eip_allocation['AllocationId']
        public_ip = eip_allocation['PublicIp']
        print(f"Using Elastic IP: {public_ip}")
        
        # Disassociate previous instance if already associated
        if 'AssociationId' in eip_allocation:
            ec2.disassociate_address(AssociationId=eip_allocation['AssociationId'])
            print("Disassociated IP from previous instance.")
            # Wait briefly for disassociation to complete
            time.sleep(5)
    else:
        # Try to allocate a new EIP - this might fail if quota is exceeded
        print("No available Elastic IPs found. Attempting to allocate a new one...")
        try:
            eip = ec2.allocate_address(Domain='vpc')
            allocation_id = eip['AllocationId']
            public_ip = eip['PublicIp']
            print("Elastic IP allocated:", public_ip)

            ec2.create_tags(
                Resources=[allocation_id], 
                Tags=[{'Key': 'Name', 'Value': 'BackendEIP'}]
            )
            print("Elastic IP tagged: BackendEIP")
        except ClientError as e:
            if 'AddressLimitExceeded' in str(e):
                print("⚠️ Elastic IP quota exceeded and no unassociated IPs found.")
                print("Please release unused Elastic IPs or request a quota increase.")
                print("Your instance has been created but does not have a fixed IP.")
                
                # Get the current public IP of the instance (this will change if the instance is stopped/started)
                instance_details = ec2.describe_instances(InstanceIds=[instance_id])
                temp_public_ip = instance_details['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'No public IP')
                print(f"Current temporary public IP: {temp_public_ip}")
                
                # Create connection and setup scripts
                key_name = instance_details['Reservations'][0]['Instances'][0]['KeyName']
                connect_script = f"""#!/bin/bash
# WARNING: This instance does not have a fixed Elastic IP
# The current public IP will change if the instance is stopped and started
# Current public IP: {temp_public_ip}
ssh -i "{key_name}.pem" ubuntu@{temp_public_ip}
"""
                setup_script = f"""#!/bin/bash
# Setup script for Ubuntu server
echo "Setting up your Travel Memory application server..."

# Connect to the server
ssh -i "{key_name}.pem" ubuntu@{temp_public_ip} '
    # Update package lists
    sudo apt update
    
    # Install Node.js (using NodeSource for more recent version)
    echo "Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Install MongoDB
    echo "Installing MongoDB..."
    sudo apt install -y mongodb
    sudo systemctl start mongodb
    sudo systemctl enable mongodb
    
    # Install Nginx
    echo "Installing Nginx..."
    sudo apt install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Install git
    echo "Installing git..."
    sudo apt install -y git
    
    # Create application directory
    echo "Setting up application directory..."
    mkdir -p ~/travel-memory-app
    
    # Check versions
    echo "Installed versions:"
    echo "Node.js: $(node -v)"
    echo "npm: $(npm -v)"
    echo "MongoDB: $(mongod --version | head -n 1)"
    echo "Nginx: $(nginx -v 2>&1)"
    echo "Git: $(git --version)"
    
    echo "Setup complete!"
'
"""
                with open("connect-to-ec2.sh", "w", newline='\n', encoding='utf-8') as f:
                    f.write(connect_script)
                with open("setup-server.sh", "w", newline='\n', encoding='utf-8') as f:
                    f.write(setup_script)
                    
                print("\n✅ Connection script 'connect-to-ec2.sh' created with warning.")
                print("✅ Setup script 'setup-server.sh' created.")
                print(f"\n⚠️ DEPLOYMENT COMPLETE WITH TEMPORARY IP!")
                print(f"Instance ID: {instance_id}")
                print(f"Temporary Public IP: {temp_public_ip}")
                print(f"SSH Command: ssh -i '{key_name}.pem' ubuntu@{temp_public_ip}")
                print(f"NOTE: This IP will change if you stop and start the instance!")
                exit(0)
            else:
                raise
    
    # Associate the EIP with the instance
    try:
        ec2.associate_address(InstanceId=instance_id, AllocationId=allocation_id)
        print("Elastic IP associated successfully.")
    except ClientError as e:
        print(f"Error associating Elastic IP: {str(e)}")
        raise

    time.sleep(3)

    # Get instance details
    instance_details = ec2.describe_instances(InstanceIds=[instance_id])
    instance_name = "unnamed"
    for tag in instance_details['Reservations'][0]['Instances'][0].get('Tags', []):
        if tag['Key'] == 'Name':
            instance_name = tag['Value']
            
    # Create connection and setup scripts
    key_name = instance_details['Reservations'][0]['Instances'][0]['KeyName']
    connect_script = f"""#!/bin/bash
# Connection script for {instance_name} ({instance_id})
# Fixed Elastic IP: {public_ip}
ssh -i "{key_name}.pem" ubuntu@{public_ip}
"""

    setup_script = f"""#!/bin/bash
# Setup script for Ubuntu server
echo "Setting up your Travel Memory application server..."

# Connect to the server
ssh -i "{key_name}.pem" ubuntu@{public_ip} '
    # Update package lists
    sudo apt update
    
    # Install Node.js (using NodeSource for more recent version)
    echo "Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Install MongoDB
    echo "Installing MongoDB..."
    sudo apt install -y mongodb
    sudo systemctl start mongodb
    sudo systemctl enable mongodb
    
    # Install Nginx
    echo "Installing Nginx..."
    sudo apt install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Install git
    echo "Installing git..."
    sudo apt install -y git
    
    # Create application directory
    echo "Setting up application directory..."
    mkdir -p ~/travel-memory-app
    
    # Check versions
    echo "Installed versions:"
    echo "Node.js: $(node -v)"
    echo "npm: $(npm -v)"
    echo "MongoDB: $(mongod --version | head -n 1)"
    echo "Nginx: $(nginx -v 2>&1)"
    echo "Git: $(git --version)"
    
    echo "Setup complete!"
'
"""

    with open("connect-to-ec2.sh", "w", newline='\n', encoding='utf-8') as f:
        f.write(connect_script)
    with open("setup-server.sh", "w", newline='\n', encoding='utf-8') as f:
        f.write(setup_script)
    
    print("\n✅ Connection script 'connect-to-ec2.sh' created successfully.")
    print("✅ Setup script 'setup-server.sh' created successfully.")
    
    print(f"\n✅ DEPLOYMENT COMPLETE!")
    print(f"Instance ID: {instance_id}")
    print(f"Public IP (Elastic IP): {public_ip}")
    print(f"SSH Command: ssh -i '{key_name}.pem' ubuntu@{public_ip}")
    print(f"To set up the server: ./setup-server.sh")

except Exception as e:
    print(f"Unexpected error: {str(e)}")
    raise