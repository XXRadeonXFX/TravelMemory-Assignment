import boto3

ec2 = boto3.client('ec2')
response = ec2.create_key_pair(KeyName='TMKeyPrinceFrontend')
with open("TMKeyPrinceFrontend.pem", "w") as file:
    file.write(response['KeyMaterial'])
