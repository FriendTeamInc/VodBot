import requests

def gql_query(query=None, data=None):
	gql_url = "https://gql.twitch.tv/gql"

	# We use Twitch's private client ID for GQL calls
	headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

	resp = requests.post(gql_url, json={"query":query}, data=data, headers=headers)
	if 400 <= resp.status_code < 500:
		data = resp.json()
		raise Exception(data["message"]) # TODO: make exceptions?
	resp.raise_for_status()

	if "errors" in resp:
		raise Exception(response["errors"])

	return resp

VIDEO_ACCESS_QUERY = """
{{
	videoPlaybackAccessToken(
		id: {video_id},
		params: {{
			platform: "web",
			playerBackend: "mediaplayer",
			playerType: "site"
		}}
	) {{
		signature
		value
	}}
}}
"""

def get_access_token(video_id):
	"""
	Gets the VOD player access token, used to stream the VOD to the host.
	"""
	query = VIDEO_ACCESS_QUERY.format(video_id=video_id)

	resp = gql_query(query=query).json()

	return resp["data"]["videoPlaybackAccessToken"]

CLIP_SOURCE_QUERY = """
{{
	clip(slug: "{}") {{
		id
		slug
		title
		createdAt
		viewCount
		durationSeconds
		url
		videoQualities {{
			frameRate
			quality
			sourceURL
		}}
		game {{
			id
			name
		}}
		broadcaster {{
			displayName
			login
		}}
	}}
}}
"""

def get_clip_source(clip_id):
	query = CLIP_SOURCE_QUERY.format(clip_id)

	resp = gql_query(query=query).json()

	return resp["data"]["clip"]["videoQualities"][0]["sourceURL"]
