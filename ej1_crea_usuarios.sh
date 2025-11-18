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
done < "$archivousu"

###########################
###INFORMACION A MOSTRAR###
###########################

if [ "$flaginfo" -eq 1 ]; then
	echo "Se han creado $contadorusuok usuarios con éxito."
fi
