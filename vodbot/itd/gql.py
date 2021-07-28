# Module to call GQL queries

from urllib import parse
from vodbot import TWITCH_CLIENT_ID

import requests
from urllib.parse import urlencode


GQL_URL = "https://gql.twitch.tv/gql"
GQL_HEADERS = {"Client-ID": TWITCH_CLIENT_ID} # We use Twitch's private client ID for GQL calls


def _process_query_errors(resp):
	if 400 <= resp.status_code < 500:
		data = resp.json()
		raise Exception(data["message"]) # TODO: make exceptions?
	resp.raise_for_status()

	if "errors" in resp:
		raise Exception(resp["errors"])


def gql_get(params={}):
	resp = requests.get(GQL_URL, params=params, headers=GQL_HEADERS)
	_process_query_errors(resp)
	return resp


def gql_post(data=None, json=None):
	resp = requests.post(GQL_URL, data=data, json=json, headers=GQL_HEADERS)
	_process_query_errors(resp)
	return resp


def gql_query(query=None, data=None):
	resp = requests.post(GQL_URL, json={"query":query}, data=data, headers=GQL_HEADERS)
	_process_query_errors(resp)
	return resp

# GQL Query forms
# Channel VODs query
GET_CHANNEL_VIDEOS_QUERY = """
{{
	user(login: "{channel_id}") {{
		videos(
			first: {first},
			type: {type},
			sort: {sort},
			after: "{after}",
			options: {{
				gameIDs: []
			}}
		) {{
			totalCount
			pageInfo {{
				hasNextPage
				hasPreviousPage
			}}
			edges {{
				cursor
				node {{
					id
					title
					publishedAt
					broadcastType
					lengthSeconds
					thumbnailURLs
					game {{
						name
					}}
					creator {{
						id
						login
						displayName
					}}
				}}
			}}
		}}
	}}
}}
"""
# Channel Clips query
# period can be LAST_DAY, LAST_WEEK, LAST_MONTH, or ALL_TIME
GET_CHANNEL_CLIPS_QUERY = """
{{
	user(login: "{channel_id}") {{
		clips(
			first: {first},
			after: "{after}",
			criteria: {{ period: ALL_TIME, sort: VIEWS_DESC }}
			) {{
			pageInfo {{
				hasNextPage
			}}
			edges {{
				cursor
				node {{
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
						id
						displayName
						login
					}}
					curator {{
						id
						displayName
						login
					}}
				}}
			}}
		}}
	}}
}}
"""
# Single VOD query
GET_VIDEO_QUERY = """
{{
	video(id: "{video_id}") {{
		id
		title
		publishedAt
		broadcastType
		lengthSeconds
		game {{
			name
		}}
		creator {{
			login
			displayName
		}}
	}}
}}
"""
# Single Clip query
GET_CLIP_QUERY = """
{{
	clip(slug: "{clip_slug}") {{
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
# Channel info query
GET_CHANNEL_QUERY = """
{{
	user(login: "{channel_id}") {{
		id
		login
		displayName
		description
		createdAt
		roles {{
			isPartner
		}}
		stream {{
			id
			title
			type
			viewersCount
			createdAt
			game {{
				name
			}}
		}}
	}}
}}
"""


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


def get_clip_source(clip_slug):
	query = GET_CLIP_QUERY.format(clip_slug=clip_slug)

	resp = gql_query(query=query).json()

	url = resp["data"]["clip"]["videoQualities"][0]["sourceURL"]

	query = {
		"operationName": "VideoAccessToken_Clip",
		"variables": {
			"slug": clip_slug
		},
		"extensions": {
			"persistedQuery": {
				"version": 1,
				"sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"
			}
		}
	}

	resp = gql_post(json=query).json()
	token = resp["data"]["clip"]["playbackAccessToken"]
	token = urlencode({
		"sig": token["signature"],
		"token": token["value"]
	})

	url = f"{url}?{token}"

	return url
