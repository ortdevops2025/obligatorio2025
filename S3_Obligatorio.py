import boto3
from botocore.exceptions import ClientError

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
    #CUIDADO CAMBIAR RUTA PARA QUE SEA UNIVERSAL
    s3.upload_file('/aplicacion/app.css', bucket_name, 'app.css')
    s3.upload_file('/aplicacion/app.js', bucket_name, 'app.js')
    s3.upload_file('/aplicacion/config.php', bucket_name, 'config.php')
    s3.upload_file('/aplicacion/index.html', bucket_name, 'index.html')
    s3.upload_file('/aplicacion/index.php', bucket_name, 'index.php')
   # s3.upload_file('/aplicacion/init_db.sql', bucket_name, 'init_db.sql')
    s3.upload_file('/aplicacion/login.css', bucket_name, 'login.css')
    s3.upload_file('/aplicacion/login.html', bucket_name, 'login.html')
    s3.upload_file('/aplicacion/login.js', bucket_name, 'login.js')
    s3.upload_file('/aplicacion/login.php', bucket_name, 'login.php')
 #   s3.upload_file('/aplicacion/README.md', bucket_name, 'README.md')

    print("Archivos subidos correctamente.")
except ClientError as e:
    print(f"Error subiendo archivo: {e}")