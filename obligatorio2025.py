import boto3
import botocore.exceptions as ClientError
import os
from botocore.exceptions import ClientError

#SECCION DE S3

s3 = boto3.client('s3')

bucket_name = 'obligatorio2025qwertyuiop'

# Crear el bucket
try:
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket creado: {bucket_name}")
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f"El bucket {bucket_name} ya existe y es tuyo.")
    else:
        print(f"Error creando bucket: {e}")
        exit(1)

# Subir los archivos de la aplicacion
try:
    s3.upload_file('aplicacion/app.css', bucket_name, 'app.css')
    s3.upload_file('aplicacion/app.js', bucket_name, 'app.js')
    s3.upload_file('aplicacion/config.php', bucket_name, 'config.php')
    s3.upload_file('aplicacion/index.html', bucket_name, 'index.html')
    s3.upload_file('aplicacion/index.php', bucket_name, 'index.php')
    s3.upload_file('aplicacion/init_db.sql', bucket_name, 'init_db.sql')
    s3.upload_file('aplicacion/login.css', bucket_name, 'login.css')
    s3.upload_file('aplicacion/login.html', bucket_name, 'login.html')
    s3.upload_file('aplicacion/login.js', bucket_name, 'login.js')
    s3.upload_file('aplicacion/login.php', bucket_name, 'login.php')
 #   s3.upload_file('/aplicacion/README.md', bucket_name, 'README.md')

    print("Archivos subidos correctamente.")
except ClientError as e:
    print(f"Error subiendo archivo: {e}")

#SECCION RDS##################################################

print(f'Ingresar passord maestro de la base')
RDS_ADMIN_PASSWORD = input()
os.environ['RDS_ADMIN_PASSWORD'] = RDS_ADMIN_PASSWORD

# Parámetros
rds = boto3.client('rds')
DB_INSTANCE_ID = 'app-mysql'
DB_NAME = 'app'
DB_USER = 'admin'
# La password debe venir de una variable de entorno
DB_PASS = os.environ.get('RDS_ADMIN_PASSWORD')

if not DB_PASS:
   raise Exception('Debes definir la variable de entorno RDS_ADMIN_PASSWORD con la contraseña del admin.')

try:
    rds.create_db_instance(
        DBInstanceIdentifier=DB_INSTANCE_ID,
        AllocatedStorage=20,
        DBInstanceClass='db.t3.medium',
        Engine='mariadb',
        MasterUsername=DB_USER,
        MasterUserPassword=DB_PASS,
        DBName=DB_NAME,
        PubliclyAccessible=True,
        BackupRetentionPeriod=0
    )
    print(f'Instancia RDS {DB_INSTANCE_ID} creada correctamente.')
except rds.exceptions.DBInstanceAlreadyExistsFault:
    print(f'La instancia {DB_INSTANCE_ID} ya existe.')

#SECCION EC2#####################################################

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
mv /var/www/html/init_db.sql /tmp/ #cambia la base a otra ruta

mysql -h <endpoint-rds> -u {DB_USER} -p{MasterUserPassword} {DB_NAME} < /tmp/init_db.sql

sudo tee /var/www/.env >/dev/null <<'ENV'
   DB_HOST=<ENDPOINT>
   DB_NAME=<DB_NAME>
   DB_USER=<DB_USER>
   DB_PASS=<$RDS_ADMIN_PASSWORD>
   
   ENV
   
   sudo chown apache:apache /var/www/.env
   sudo chmod 600 /var/www/.env```

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


#SECCION SECURITYU GROUPS###############################

#Security Group de EC2
ec2 = boto3.client('ec2')
# 1. Crear un Security Group que permita tráfico web desde cualquier IP
sg_name = 'web-sg-boto3'
try:
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description='Permitir trafico web desde cualquier IP'
    )
    sg_id = response['GroupId']
    print(f"Security Group creado: {sg_id}")
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
except ClientError as e:
    if 'InvalidGroup.Duplicate' in str(e):
        sg_id = ec2.describe_security_groups(GroupNames=[sg_name])['SecurityGroups'][0]['GroupId']
        print(f"Security Group ya existe: {sg_id}")
    else:
        raise

# 2. Asociar el SG a la instancia EC2 creada anteriormente

# Obtener la primera instancia EC2 cuyo tag Name sea 'webserver-devops'
instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['webserver-devops']}])
instance_id = None
for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        break
    if instance_id:
        break
if not instance_id:
    raise Exception("No se encontró ninguna instancia con el tag 'webserver-devops'.")

ec2.modify_instance_attribute(InstanceId=instance_id, Groups=[sg_id])
print(f"SG {sg_id} asociado a la instancia {instance_id}")

print("Ahora navegue a la IP pública de la instancia para verificar el acceso web.")

#SEcurituy Group de RDS