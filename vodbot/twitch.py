# Module to make API calls to Twitch.tv

from .channel import Channel

import requests


def get_access_token(CLIENT_ID, CLIENT_SECRET):
	"""
	Uses a (blocking) HTTP request to retrieve an access token for use with Twitch's API

	:param CLIENT_ID: The associated client ID of the Twitch Application, registered at the Twitch Dev Console online and stored in the appropriate vodbot config.
	:param CLIENT_SECRET: The associate client secret, from the same as client ID.
	:returns: The string of the access token (not including the "Bearer: " prefix).
	"""

	url = "https://id.twitch.tv/oauth2/token?client_id={id}&client_secret={secret}&grant_type=client_credentials"
	resp = requests.post(url.format(id=CLIENT_ID, secret=CLIENT_SECRET))

	accesstoken = None
	
	# Some basic checks
	if resp.status_code != 200:
		util.exit_prog(33, f"Failed to get access token from Twitch. Status: {response.status_code}")
	try:
		accesstokenjson = resp.json()
	except ValueError:
		util.exit_prog(34, f"Could not parse response json for access token.")

	if "access_token" in accesstoken_json:
		accesstoken = accesstoken_json["access_token"]
	else:
		exit_prog(4, "Could not get access token! Check your Client ID/Secret.")
		
	headers = {"Client-ID": CLIENT_ID, "Authorization": "Bearer " + ACCESS_TOKEN}
	
	return headers

def get_channels(channel_ids, headers):
	"""
	Uses a (blocking) HTTP request to retrieve channel information from Twitch API.

	:param channel_ids: A list of channel login name strings.
	:param headers: The headers returned from get_access_token.
	:returns: A list of Channel objects.
	"""

	url = "https://api.twitch.tv/helix/users?" + "&".join(f"login={i}" for i in channel_ids)
	resp = requests.get(url, headers=headers)

	# Some basic checks
	if resp.status_code != 200:
		util.exit_prog(5, f"Failed to get user ID's from Twitch. Status: {response.status_code}")
	try:
		resp = resp.json()
	except ValueError:
		util.exit_prog(12, f"Could not parse response json for user ID's.")
	
	# Make channel objects and store them in a list
	channels = []
	for i in resp["data"]:
		channels.append(Channel(i))
	
	return channels
