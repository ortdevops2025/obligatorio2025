# obligatorio2025
Repositorio para obligatorio de DevOps Universidad ORT 2025 Sosa - Pintos

NOTA: Documentacion mas detallada puede encontrarse en el archivo "Sosa_Pintos_Obligatorio2025DevOps.pdf" el cual se encuntra en este mismo repositorio:

LINK

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
#########VALIDAR ARCHIVO #############
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

		if id "$USUARIO" >/dev/null 2>&1
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
			useradd -m -c "$COMENTARIO" -d "$HOME" -s "$SHELL" "$USUARIO" >/dev/null 2>&1
		else
			useradd -M -c "$COMENTARIO" -d "$HOME" -s "$SHELL" "$USUARIO" >/dev/null 2>&1
		fi

		if [ $? -eq 0 ] #verifica que el comando de agregar usuario haya sido exitoso
		then
			if [ -n "$password" ]
			then
				echo "$USUARIO:$password" | chpasswd 2>/dev/null
			fi

			contadorusuok=$((contadorusuok + 1)) #Sumo uno si se agrego el usuario correctamente

			if [ "$flaginfo" -eq 1 ]; then #Muestra informacion si se uso el parametro -i
			
				echo "Usuario $USUARIO creado con éxito con datos indicados:"
				echo "Comentario: ${COMENTARIO:-<valor por defecto>}"
				echo "Dir home: ${HOME:-<valor por defecto>}"
				echo "Asegurado existencia de directorio home: ${CREARHOME:-<valor por defecto>}"
				echo "Shell por defecto: ${SHELL:-<valor por defecto>}"
				echo
			fi
		else
			echo "ATENCION: el usuario $USUARIO no pudo ser creado"
		fi
	fi	
done

###########################
###INFORMACION A MOSTRAR###
###########################

if [ "$flaginfo" -eq 1 ]; then
	echo "Se han creado $contadorusuok usuarios con éxito."
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



