import boto3
from botocore.exceptions import ClientError
import time
import os

# SECCION S3 - Creacion de bucket y copia de archivos
s3 = boto3.client('s3')

bucket_name = 'obligatorio2025qwertyuiop'

# Crea el bucket si no exsite
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

    print("Archivos subidos correctamente.")
except ClientError as e:
    print(f"Error subiendo archivo: {e}")

# CREACION de variables de base de datos

print("Ingresar password maestro de la base:")
RDS_ADMIN_PASSWORD = input() #Esto hace que no sea necesario hardcodear el password en el codigo
os.environ["RDS_ADMIN_PASSWORD"] = RDS_ADMIN_PASSWORD


DB_INSTANCE_ID = "app-mysql"
DB_NAME = "demo_db"  #Nombre sacado del archivo sql de ejemplo de la aplicacion, si es diferente no funciona sin modificar el .sql
DB_USER = "admin"
DB_PASS = RDS_ADMIN_PASSWORD

#Se comienzan a crear las instancuas de EC2 y RDS
rds = boto3.client('rds')

ec2 = boto3.client('ec2')


####################################
#Creacion de Grupos de Seguridad####
####################################


sg_name = "web-sg-boto3"
sg_rds_name = "rds-sg-boto3"

# Grupo de Seguridad de EC2
try:
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description="Permitir trafico web desde cualquier IP"
    )
    sg_ec2 = response["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=sg_ec2,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )
    print(f"SG EC2 creado: {sg_ec2}")
except ClientError as e:
    if "InvalidGroup.Duplicate" in str(e):
        sg_ec2 = ec2.describe_security_groups(GroupNames=[sg_name])['SecurityGroups'][0]['GroupId']
        print(f"SG EC2 ya existe: {sg_ec2}")
    else:
        raise

# SG RDS
try:
    response = ec2.create_security_group(
        GroupName=sg_rds_name,
        Description="ACCESSSQL"
    )
    sg_rds = response["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=sg_rds,
        IpPermissions=[{
            "IpProtocol": "tcp",
            "FromPort": 3306,
            "ToPort": 3306,
            "UserIdGroupPairs": [{"GroupId": sg_ec2}]
        }]
    )
    print(f"SG RDS creado: {sg_rds}")
except ClientError as e:
    if "InvalidGroup.Duplicate" in str(e):
        sg_rds = ec2.describe_security_groups(GroupNames=[sg_rds_name])["SecurityGroups"][0]["GroupId"]
        print(f"SG RDS ya existe: {sg_rds}")
    else:
        raise

#################################
##Creacion de instancia de DB RDS
#################################

try:
    rds.create_db_instance(
        DBInstanceIdentifier=DB_INSTANCE_ID,
        AllocatedStorage=20,
        DBInstanceClass='db.t3.medium',
        Engine='mariadb',
        MasterUsername=DB_USER,
        MasterUserPassword=DB_PASS,
        DBName=DB_NAME,
        VpcSecurityGroupIds=[sg_rds],
        PubliclyAccessible=False,
        BackupRetentionPeriod=0
    )
    print("Creacndo instancia de RDS")
except rds.exceptions.DBInstanceAlreadyExistsFault:
    print("La instancia RDS ya existe")

# Esperar a que RDS esté disponible
print("Esperando RDS para continuar")
waiter = rds.get_waiter('db_instance_available')
waiter.wait(DBInstanceIdentifier=DB_INSTANCE_ID)
print("RDS creado y en linea")

# Obtener endpoint
rds_info = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_ID)
RDS_ENDPOINT = rds_info['DBInstances'][0]['Endpoint']['Address']
print(f"Endpoint RDS: {RDS_ENDPOINT}")

##############################
##Procesamiento de instancia de EC2
################################

#Bloque de User data con comandos para instalar las dependencias y preparacion de la aplicacion
user_data = f'''#!/bin/bash

dnf clean all
dnf makecache
dnf -y update

dnf -y install httpd php php-cli php-fpm php-common php-mysqlnd mariadb105

systemctl enable --now httpd
systemctl enable --now php-fpm

echo '<FilesMatch \\.php$>
  SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost/"
</FilesMatch>' > /etc/httpd/conf.d/php-fpm.conf

aws s3 sync s3://{bucket_name} /var/www/html/

mv /var/www/html/init_db.sql /var/www/init_db.sql

for i in {{1..20}}; do
    mysql -h {RDS_ENDPOINT} -u {DB_USER} -p{DB_PASS} -e "SELECT 1;" {DB_NAME} && break
    sleep 5
done

mysql -h {RDS_ENDPOINT} -u {DB_USER} -p{DB_PASS} {DB_NAME} < /var/www/init_db.sql

cat << 'EOF' > /var/www/.env
DB_HOST={RDS_ENDPOINT}
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASS={DB_PASS}

APP_USER=admin
APP_PASS=admin123
EOF

chown apache:apache /var/www/.env
chmod 600 /var/www/.env

chmod -R 755 /var/www/html
chown -R apache:apache /var/www/html

systemctl restart httpd
systemctl restart php-fpm
'''

response = ec2.run_instances(
    ImageId='ami-06b21ccaeff8cd686',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[sg_ec2],
    IamInstanceProfile={'Name': 'LabInstanceProfile'},
    UserData=user_data
)

instance_id = response['Instances'][0]['InstanceId']
print(f"Instancia EC2 creada: {instance_id}")

ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': 'webserver-devops'}])

print("Esperando a que EC2 este listo")
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])

print("EC2 esta listo, ya puede navegar en el sitio")
print("SG listos y asignados a EC2 y RDS")
print("Navegue a la IP pública del EC2 cuando esté disponible")
