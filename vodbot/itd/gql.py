import requests

def gql_query(client_id, data):
	gql_url = "https://gql.twitch.tv/gql"

	headers = {"Client-ID": client_id}

	resp = requests.post(gql_url, data=data, headers=headers)
	if 400 <= resp.status_code < 500:
		data = resp.json()
		raise Exception(data["message"]) # TODO: make exceptions?
	resp.raise_for_status()

	if "errors" in response:
		raise Exception(response["errors"])

	return
