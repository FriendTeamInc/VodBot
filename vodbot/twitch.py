# Module to make API calls to Twitch.tv

from .channel import Channel
from .clip import Clip
from .video import Video

import requests


def get_access_token(CLIENT_ID, CLIENT_SECRET):
	"""
	Uses a (blocking) HTTP request to retrieve an access token for use with Twitch's API.

	:param CLIENT_ID: The associated client ID of the Twitch Application, registered at the Twitch Dev Console online and stored in the appropriate vodbot config.
	:param CLIENT_SECRET: The associate client secret, from the same as client ID.
	:returns: The string of the access token (not including the "Bearer: " prefix).
	"""

	url = "https://id.twitch.tv/oauth2/token?client_id={id}&client_secret={secret}&grant_type=client_credentials"
	resp = requests.post(url.format(id=CLIENT_ID, secret=CLIENT_SECRET))
	
	# Some basic checks
	if resp.status_code != 200:
		util.exit_prog(33, f"Failed to get access token from Twitch. Status: {resp.status_code}")
	
	# Try to decode response
	accesstoken_json = None
	try:
		accesstoken_json = resp.json()
	except ValueError:
		util.exit_prog(34, f"Could not parse response json for access token.")

	# Try to pull access token from response
	accesstoken = None
	if "access_token" in accesstoken_json:
		accesstoken = accesstoken_json["access_token"]
	else:
		exit_prog(4, "Could not get access token! Check your Client ID/Secret.")
		
	headers = {"Client-ID": CLIENT_ID, "Authorization": "Bearer " + accesstoken}
	
	return headers


def get_channels(channel_ids, headers):
	"""
	Uses a (blocking) HTTP request to retrieve channel information from Twitch's API.

	:param channel_ids: A list of channel login name strings.
	:param headers: The headers returned from get_access_token.
	:returns: A list of Channel objects.
	"""

	url = "https://api.twitch.tv/helix/users?" + "&".join(f"login={i}" for i in channel_ids)
	resp = requests.get(url, headers=headers)

	# Some basic checks
	if resp.status_code != 200:
		util.exit_prog(5, f"Failed to get user ID's from Twitch. Status: {resp.status_code}")
	try:
		resp = resp.json()
	except ValueError:
		util.exit_prog(12, f"Could not parse response json for user ID's.")
	
	# Make channel objects and store them in a list
	channels = []
	for i in resp["data"]:
		channels.append(Channel(i))
	
	return channels


def get_channel_vods(channel: Channel, headers: dict):
	"""
	Uses a (blocking) HTTP request to retrieve VOD info for a specific channel.

	:param channel: A Channel object.
	:param headers: The headers returned from get_access_token.
	:returns: A list of VOD objects.
	"""
	url = "https://api.twitch.tv/helix/videos?user_id={video_id}&first=100&type=archive"
	return _get_channel_content(url, "VOD", channel, headers)


def get_channel_clips(channel, headers):
	"""
	Uses a (blocking) HTTP request to retrieve Clip info for a specific channel.

	:param channel: A Channel object.
	:param headers: The headers returned from get_access_token.
	:returns: A list of Clip objects.
	"""
	url = "https://api.twitch.tv/helix/clips?broadcaster_id={video_id}&first=100"
	return _get_channel_content(url, "Clip", channel, headers)


def _get_channel_content(video_url, noun, channel, headers):
	# List of videos to return
	videos = []
	# Deal with pagination
	pagination = ""
	while True:
		# generate URL
		url = video_url.format(video_id=channel.id)
		if pagination != "":
			url += "&after=" + pagination
		resp = requests.get(url, headers=headers)

		# Some basic checks
		if resp.status_code != 200:
			util.exit_prog(5, f"Failed to get {noun} data from Twitch. Status: {resp.status_code}")
		try:
			resp = resp.json()
		except ValueError:
			util.exit_prog(9, f"Could not parse response json for {channel.display_name}'s {contentnoun}s.")
		
		# Break out if we went through all the videos
		if len(resp["data"]) == 0:
			break

		# Add VODs to list to download later.
		for vod in resp["data"]:
			# We need to ignore live VOD's
			# Live VODs don't have thumbnails
			if vod["thumbnail_url"] != "":
				if noun == "VOD":
					videos.append(Video(vod))
				elif noun == "Clip":
					videos.append(Clip(vod))
		
		# If there's no other cursors, let's break.
		if "cursor" in resp["pagination"]:
			pagination = resp["pagination"]["cursor"]
		else:
			break
	
	return videos
