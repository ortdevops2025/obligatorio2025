import boto3

# Crear cliente EC2
ec2 = boto3.client('ec2')


user_data = '''#!/bin/bash
sudo yum update -y
sudo amazon-linux-extras enable php8.2
sudo yum clean metadata
sudo yum install -y httpd php php-mysqli mariadb105-server-utils.x86_64
sudo systemctl enable httpd
sudo systemctl start httpd


# Descargar archivos desde S3 al directorio web
aws s3 sync s3://obligatorio2025qwertyuiop /var/www/html/

# Permisos para los archivos

chmod -R 755 /var/www/html
chown -R apache:apache /var/www/html
'''


# Crear la instancia EC2
response = ec2.run_instances(
    ImageId='ami-06b21ccaeff8cd686',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    IamInstanceProfile={'Name': 'LabInstanceProfile'},  # Debe tener permiso s3:GetObject
    UserData=user_data
)

instance_id = response['Instances'][0]['InstanceId']

# Agregar tag - webserver-devops
ec2.create_tags(
    Resources=[instance_id],
    Tags=[{'Key': 'Name', 'Value': 'webserver-devops'}]
)

print(f" Instancia creada con ID: {instance_id} y tag 'webserver-devops'")
print(" Los archivos del bucket S3 serán copiados automáticamente a /var/www/html/")