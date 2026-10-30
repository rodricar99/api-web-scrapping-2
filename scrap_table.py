import json
import requests

# Servicio GraphQL (AppSync) que usa la página del IGP, tomado de su configuración pública
GRAPHQL_URL = "https://vgsq5e345rbslkzskqx6efewsu.appsync-api.us-east-1.amazonaws.com/graphql"
API_KEY = "da2-dauvp6fdtngv3p55rt7buu6r2e"

# Consulta de introspección: lista las consultas (queries) que expone el servicio
INTROSPECTION_QUERY = """
{
  __schema {
    queryType {
      fields {
        name
        args { name type { kind name ofType { kind name } } }
      }
    }
  }
}
"""


def lambda_handler(event, context):
    response = requests.post(
        GRAPHQL_URL,
        headers={"Content-Type": "application/json", "x-api-key": API_KEY},
        data=json.dumps({"query": INTROSPECTION_QUERY}),
        timeout=20,
    )

    return {
        'statusCode': response.status_code,
        'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
    }
