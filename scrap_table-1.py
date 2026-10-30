import requests
from bs4 import BeautifulSoup
import boto3
import uuid

URL = "https://ultimosismo.igp.gob.pe/productos/reportes-sismicos"
TABLE_NAME = "TablaSismosIGP"


def lambda_handler(event, context):
    # Realizar la solicitud HTTP a la página del IGP
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    if response.status_code != 200:
        return {
            'statusCode': response.status_code,
            'body': 'Error al acceder a la página web del IGP'
        }

    # Parsear el HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar la primera tabla de reportes sísmicos
    table = soup.find('table')
    if not table:
        return {
            'statusCode': 404,
            'body': 'No se encontró la tabla en la página del IGP'
        }

    # Extraer los encabezados (th) de la tabla
    headers = [th.get_text(strip=True) for th in table.find_all('th')]

    # Extraer las filas de datos (solo las que tienen celdas td)
    rows = []
    for tr in table.find_all('tr'):
        cells = tr.find_all('td')
        if not cells:
            continue
        values = [td.get_text(strip=True) for td in cells]
        # Si no hay encabezados suficientes, usar nombres genéricos
        names = headers if len(headers) == len(values) else [f"columna_{j+1}" for j in range(len(values))]
        rows.append({names[j] or f"columna_{j+1}": v for j, v in enumerate(values)})

    # Guardar en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    db_table = dynamodb.Table(TABLE_NAME)

    # Eliminar los elementos anteriores
    scan = db_table.scan()
    with db_table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(Key={'id': each['id']})

    # Insertar los nuevos datos
    i = 1
    for row in rows:
        row['#'] = i
        row['id'] = str(uuid.uuid4())
        db_table.put_item(Item=row)
        i += 1

    return {
        'statusCode': 200,
        'body': rows
    }
