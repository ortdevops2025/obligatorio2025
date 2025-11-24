# Obligatorio2025 - Analista en Infraestructura Informatica - UNIVERSIDAD ORT
Repositorio para obligatorio de DevOps Universidad ORT 2025 Sosa - Pintos

NOTA: Documentacion mas detallada puede encontrarse en el archivo "Sosa_Pintos_Obligatorio2025DevOps.pdf" el cual se encuntra en este mismo repositorio:

https://github.com/ortdevops2025/obligatorio2025/blob/main/Sosa_Pintos_Obligatorio2025DevOps.pdf

<img width="469" height="165" alt="image" src="https://github.com/user-attachments/assets/e46fa13c-ae44-4f9f-b783-6b02120454a2" />

En el documento PDF encontrara detalles sobre:
Declaracion de autoria
Bibliografia (Incluido prompts utilizados con Inteligencia artificial generativa)
Problemas encontrados
Conclusiones finales

SECCION I - SCRIPT DE BASH

Para la realización y pruebas de este script fue utilizada la máquina virtual de CentOS 8 proporcionada en el curso con algunas actualizaciones.

Version de CentOS:
 <img width="333" height="65" alt="image" src="https://github.com/user-attachments/assets/0024646f-2343-4775-a4ec-4cbabe94bcb1" />

Se muestra a continuación el script que esta adjunto en el repositorio.

```
################################################################################

#!/bin/bash
#Fecha Modificado 24/11/2025

flaginfo=0         # Variable para -i vale distinto de 0 se muestra flaginforamcion
password=""    # Variable para -c que guarda el password
archivousu=""     # archivo con la lista de usuarios
contadorusuok=0    # Contador de usuarios creados OK


######################################
######Comprobacion de Parametros######
######################################

if [ "$1" = "-i" ] && [ "$2" = "-c" ] #Verifica el orden de los parametros i y c
then
  flaginfo=1
  password="$3"
  archivousu="$4"
else
	if [ "$1" = "-c" ] && [ "$3" = "-i" ] #Verifica segundo orden posible de los parametros i y c
	then
		flaginfo=1
  	 	password="$2"
  	 	archivousu="$4"
	else 
		if [ "$1" = "-i" ] #Verifica si se utilizo solo el parametro de informacion
		then
			flaginfo=1
  			archivousu="$2"
		else
			if  [ "$1" = "-c" ] #Verifica si se utilizo solo el parametro de password
		      	then
				password="$2"
  				archivousu="$3"
			else
  				archivousu="$1" #Procsa el archivo si no se utilizron parametros
			fi
		fi
	fi
fi

######################################
#########VALIDAR archivousu #############
######################################

if [ ! $# -ge 1 ] #Verifica que se usen al menos un parametro en el script
then
	echo "Debe proporcionar al menos un parametro"
	exit 2
fi

if [ ! -f "$archivousu" ] #Verifica que el archivo sea regular
then
 	echo "$archivousu no existe o no es regular" >&2
 	exit 3
fi

if [ ! -r "$archivousu" ] #Verifica que el archivo tenga read only
then
 	echo "$archivousu no tiene permiso de lectura" >&2
 	exit 4
fi

if [ "$(id -u)" -ne 0 ] #IAG Geneardo, verifica si es root el usuario al momento de ejecucion
then
	echo "Este script debe ejecutarse como root" >&2
	exit 5
fi


######################################
######DESEMPAQUETADO DE archivousu#######
######################################

IFS=$'\n' #Defino separador de lineas como el salto de linea 

for i in $(cat "$archivousu")
do

#verificador de campos de linea para que sean 5

	campos=$(echo "$i" | tr -cd ':' | wc -c) #Cuenta los delimitadores : para verificar sintaxis de la linea

    if [ "$campos" -ne 4 ]
    then
		echo "Sintaxis incorrecta del $archivousu pasado como parametro" >&2
        echo "La linea $i no contiene exactamente 5 campos separados por : " >&2
		
    else

		#Asigna valores a las variables
		
		USUARIO=$(echo "$i" | cut -d: -f1)
		COMENTARIO=$(echo "$i" | cut -d: -f2)
		HOME=$(echo "$i" | cut -d: -f3)
		CREARHOME=$(echo "$i" | cut -d: -f4 | tr '[:lower:]' '[:upper:]')
		SHELL=$(echo "$i" | cut -d: -f5-)

		# Comprobacion de existencia de usuario

		if id "$USUARIO" >/dev/null 2>&1 #el comando id retorna 0 si es exitoso o distinto de 0 si no lo es
		then
			echo "ATENCION: el usuario $USUARIO ya existe"
			continue
		fi

		# Valores por defecto

		[ -z "$SHELL" ] && SHELL="/bin/bash"
		[ -z "$HOME" ] && HOME="/home/$USUARIO"
		[ -z "$CREARHOME" ] && CREARHOME="SI"

		# Creacion del usuario

		if [ "$CREARHOME" = "SI" ]
		then
			# con -m se crea el directorio home si no existe
			useradd -m -c "$COMENTARIO" -d "$HOME" -s "$SHELL" "$USUARIO" >/dev/null 2>&1
		else
			# con -M se evita la creación del directorio home
			useradd -M -c "$COMENTARIO" -d "$HOME" -s "$SHELL" "$USUARIO" >/dev/null 2>&1
		fi

		if [ $? -eq 0 ] #verifica que el comando de agregar usuario haya sido exitoso,(exit 0)
		then
			if [ -n "$password" ] # se chequea que la variable password no este vacia
			then
				# se establece la contraseña del usuario usando chpasswd, ocultando errores
				# chpasswd asigna la contraseña al usuario leida desde la entrada estandar
				echo "$USUARIO:$password" | chpasswd 2>/dev/null
			fi

			contadorusuok=$((contadorusuok + 1)) #Sumo uno si se agrego el usuario correctamente

			if [ "$flaginfo" -eq 1 ]; then #Muestra informacion si se uso el parametro -i
			
				echo "Usuario $USUARIO creado con éxito con datos indicados:"
				# echo -e "\t" para lograr identacion
				echo -e "\tComentario: ${COMENTARIO:-<valor por defecto>}"
				echo -e "\tDir home: ${HOME:-<valor por defecto>}"
				echo -e "\tAsegurado existencia de directorio home: ${CREARHOME:-<valor por defecto>}"
				echo -e "\tShell por defecto: ${SHELL:-<valor por defecto>}"
				echo
			fi
		else
			echo "ATENCION: el usuario $USUARIO no pudo ser creado"
		fi
	fi	
#done < "$archivousu"
done

###########################
###INFORMACION A MOSTRAR###
###########################

if [ "$flaginfo" -eq 1 ]; then
	echo "Se han creado $contadorusuok usuarios con exito."
fi

################################################################################
```

PRUEBA DE USO:

Se procede a mostrar ejemplos de uso y los resultados obtenidos incluidos algunos errores testeados:

1 – Script sin Parametros:

<img width="472" height="239" alt="image" src="https://github.com/user-attachments/assets/f936c0b8-ff9f-441f-9737-9a811fffbaaf" />

En este ejemplo, al no colocarse ningún parámetro el script devuelve un resultado de error indicando que el script necesita al menos un parámetro para funcionar (el archivo)

2 – Archivo no regular

<img width="767" height="154" alt="image" src="https://github.com/user-attachments/assets/de4260a4-4a94-4589-b0d8-4f6e0f5d93d6" />

3 – Uso normal con un archivo de usuarios que tiene 3 usuarios validos para agregar y uno que ya existe:

<img width="760" height="120" alt="image" src="https://github.com/user-attachments/assets/1beee288-3ca4-4a5b-908e-981748115cc8" />

En este caso, se deberán de agregar tres usuarios, pepe, Jim Raynor y el maligno.
El usuario root ya existe por lo que el comando debería avisar de esta situacion.
Se utilizan los dos parámetros opcionales tambien -i y -c con un password 123456
Se observa en la imagen el resultado obtenido.
<img width="736" height="450" alt="image" src="https://github.com/user-attachments/assets/a0c6f9c4-2eb4-4172-a3fd-b5379d586eba" />

Archivo /etc/passwd mostrando los nuevos usuarios agregados

<img width="903" height="234" alt="image" src="https://github.com/user-attachments/assets/ed54ea89-f8b9-43c2-9af4-603bd3d82a01" />




SECCION II SCRIPT PYTHON

<img width="417" height="121" alt="image" src="https://github.com/user-attachments/assets/710a377d-ec04-4364-b3be-11dab2184643" />

Para la ejecucion del script de python, deben de satisfacerse ciertos requerimientos previos descriptos a continuacion:


Tener AWS CLI configurado / credenciales disponibles en la máquina donde ejecutes los scripts.

Suponiendo que se ejecute este proyecto desde una maquina de LINUX, se debe tener el AWS CLI instalado y confiogurado, Python 3, Pip, Boto3.

Adicionalmente debemos contar con la KEY de EC2 para el acceso de SSH si es necesario y un rol que nos permita acceder al S3.

Para ello, como ejemplo en Ubuntu AWS el cual fue utilizado ejecutamos:

```
Sudo apt update
Sudo apt upgrade
sudo apt install python3
sudo apt install python3 python3-pip -y
pip3 install boto3
sudo apt install unzip
pip3 install --upgrade --user awscli
```


Comprobacion de versiones usando como ejemplo las utilizadas:
```
apt show awscli | grep Version
aws-cli/2.13.24 Python/3.11.5 Linux/6.8.0-31-generic exe/x86_64.ubuntu.22 prompt/off
```
Tambien debemos instalar GIT para poder clonar el repositorio:
```
sudo apt install git
```
Configuramos el AWS CLI (En caso de ser necesario, con las credenciales del ambiente a utilizar)

Se utiliza el comando 
```
aws configure
```
Se pedirán los siguientes campos los cuales salen de la sesión de AWS a utilizar:

AWS Access Key ID
AWS Secret Access Key
AWS Session Token
Region Name: us-east-1 (si corresponde esa region)
Default Format: json

Ejemplo de configuracion:

<img width="1004" height="155" alt="image" src="https://github.com/user-attachments/assets/91224f4b-4b30-4839-b587-23cf514fd8c2" />
En caso de que debamos alterar algún valor, se puede correr el comando nuevamente o acceder al archivo de configuración el cual esta en texto plano en la ubicación:

/home/usuario/.aws/credentials

Instalación de agente de SSM de AWS en Ubuntu
```
sudo snap install amazon-ssm-agent –classic
```
Una vez teniendo todo configurado, clonamos el repositorio siguiente:
```
git clone https://github.com/ortdevops2025/obligatorio2025.git
```

Una vez clonado el repositorio e instalado las dependencias de la sección anterior, se debe proceder al despliegue de la instalación.

NOTA: Todos los comandos se deben ejecutar desde la carpeta /obligatorio2025, la cual es la raíz del repositorio clonado.


Desde el Directorio del repositorio clonado, ejecutar el script de instalacion y despliegue de la aplicación:
```
python3 obligatorio.py
```
<img width="1003" height="300" alt="image" src="https://github.com/user-attachments/assets/c165d099-c2b8-437e-969c-b53d329fbe9f" />

PRUEBA DE USO
Una vez finalizado el script, y la instancia de AWS correctamente iniciada, se podrá probar la aplicación ingresando al siguiente link:

http://(IP PUBLICA DE INSTANCIA)/login/php

Se utiliza el log in:
admin
admin123

Se debe desplegar correctamente la información de la aplicación:
<img width="652" height="303" alt="image" src="https://github.com/user-attachments/assets/8500b5c5-46f1-466f-a37f-d8d82c172f0b" />

DETALLE DE SCRIPT DE PYTHON
```
import boto3
from botocore.exceptions import ClientError

import os

# SECCION S3 - Creacion de bucket y copia de archivos
s3 = boto3.client('s3')

bucket_name = 'obligatorio2025qwertyuiop'

# Crea el bucket si no exsite
# En caso de existir y que sea nuestro, entra en el except y continua la ejecucion del codigo
try:
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket creado: {bucket_name}")
except ClientError as e:
    # siendo "e" la variable donde se guarda el tipo de error ocurrido
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
    # siendo "e" la variable donde se guarda el tipo de error ocurrido
    # se muestra en pantalla el error ocurrido al subir los archivos
    print(f"Error subiendo archivo: {e}")

# CREACION de variables de base de datos

# Solicitud al usuario del password maestro de la base de datos
# El password se guardara en la variable de entorno para ser usado de manera segura
# print("Ingresar password maestro de la base: ")
RDS_ADMIN_PASSWORD = input("Ingresar password maestro de la base: ") #Esto hace que no sea necesario hardcodear el password en el codigo
os.environ["RDS_ADMIN_PASSWORD"] = RDS_ADMIN_PASSWORD

# Se definen las variables de configuraion de la base de datos
DB_INSTANCE_ID = "app-mysql"
DB_NAME = "demo_db"  #Nombre sacado del archivo sql de ejemplo de la aplicacion, si es diferente no funciona sin modificar el .sql
DB_USER = "admin"
DB_PASS = RDS_ADMIN_PASSWORD

#Se comienzan a crear las instancias de EC2 y RDS
rds = boto3.client('rds')

ec2 = boto3.client('ec2')


####################################
#Creacion de Grupos de Seguridad####
####################################

# Se define nombre del security group que usaremos para la instancia ec2 y RDS
sg_name = "web-sg-boto3" 
sg_rds_name = "rds-sg-boto3" 

# Grupo de Seguridad de EC2
try:
    # Se intenta crear el security group para ec2
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description="Permitir trafico web desde cualquier IP"
    )
    # Se guarda el id del nuevo security group
    sg_ec2 = response["GroupId"]

    # Se abre el puerto 80 (http) 
    ec2.authorize_security_group_ingress(
        GroupId=sg_ec2,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}] # Se permite acceso desde cualquier IP
        }]
    )
    print(f"SG EC2 creado: {sg_ec2}")
except ClientError as e:
    # En caso de que el security group ya exista, aws devuelve en el except "InvalidGroup.Duplicate"
    if "InvalidGroup.Duplicate" in str(e):
        # En este caso entonces solo se toma el id del grupo existente en lugar de crear uno nuevo
        sg_ec2 = ec2.describe_security_groups(GroupNames=[sg_name])['SecurityGroups'][0]['GroupId']
        print(f"SG EC2 ya existe: {sg_ec2}")
    else:
        # En el caso de otro errore se detiene la ejecucion 
        raise

# SG RDS
try:
    # Se intenta crear el security group para rds
    response = ec2.create_security_group(
        GroupName=sg_rds_name,
        Description="ACCESSSQL"
    )
    sg_rds = response["GroupId"]

    # Se abre el puerto 3306 (MariaDB) solo para el security group del ec2
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
        # En este caso entonces solo se toma el id del grupo existente en lugar de crear uno nuevo
        sg_rds = ec2.describe_security_groups(GroupNames=[sg_rds_name])["SecurityGroups"][0]["GroupId"]
        print(f"SG RDS ya existe: {sg_rds}")
    else:
        # En el caso de otro errore se detiene la ejecucion
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
    print("Creando instancia de RDS")
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

#####################################
##Procesamiento de instancia de EC2##
#####################################

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
```

Uso de Inteligencia Artificial Generativa

Para la realización de este trabajo, el uso de IAG fue utilizado EXCLUSIVAMENTE para la creación de gráficos específicos o conjunto de comandos básicos con motivo de verificación.

A continuación, se detalla la lista de prompts utilizados.

IAG 1 – Sugerencia de estructura
https://chatgpt.com/
Prompt: Sugerir estructura  estructura en Bash usando if que retorne ultimo comando y analice si es 0. Si es igual a 0 dejar libre para colocar un comando una acción, sino, devolver un mensaje de éxito. 

IAG 2 – Sugerencia de estructura
https://chatgpt.com/
Prompt: Comando en linux que sirva para colocar un password automáticamente dentro de un script de bash junto a useradd

IAG 3 – Sugerencia de estructura
https://chatgpt.com/
Prompt: Ejemplo de bloque en Bash que cree usuarios con el comando adduser, compatible en ubuntu y centos.
Suponer una variable true para crear un home y un false entregaría un home por defecto.
Agregar en el ejemplo, el comentario de usuario
Utilizar if y else preferentemente

IAG 4 – Sugerencia de estructura
https://chatgpt.com/
Prompt: Como asignar valores por defecto a $SHELL o $HOME

IAG 5 – Orden de deploy
https://chatgpt.com/
Prompt: En que orden debería implementar los scripts en python con boto3 para deployar una aplicación en dos capas, la idea principal es tener, uno para ec2, otro para base de datos RDS, otro de S3 y uno para security groups 

IAG 6 – Subida de S3 a EC2
https://chatgpt.com/
Prompt: como puedo subir todos los archivos de un S3 a un directorio de una instancia EC2 usando Python y boto3

IAG6 – Variable de entorno para password
https://chatgpt.com/
Prompt: Como agregar una variable de entorno RDS_ADMIN_PASSWORD en Python para ejecutar en linux

IAG 7 – RDS Security Group
https://chatgpt.com/
Prompt: Optimizar el bloque de Script dado para el security group de RDS para el puerto 3306


IAG 8 – Wait en instancias
https://chatgpt.com/
Prompt: Ejemplo para bloque de espera en RDS o EC2 para que la instancia este lista, usar get_waiter

IAG 9 – Subida de S3 a EC2
https://chatgpt.com/
Prompt: Bloque en bash que sirva para esperar que una conexion a una base de datos sea satisfactoria con RDS

IAG 10 – Subida de S3 a EC2
https://chatgpt.com/
Prompt: Generar banner que tenga el símbolo y y el texto BASH con algún elemento discreto

IAG 11 – Formato de README.MD
https://chatgpt.com/
Prompt: (se copia el contenido del readme.md) Generar formato para README.MD de github sin modificar las imágenes insertadas o modificar el codigo fuente de BASH o PYTHON comentado. No utilizar iconos, solo formatear de manera profesional estándar el mismo.
