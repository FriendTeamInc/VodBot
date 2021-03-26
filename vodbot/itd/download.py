from . import gql
import requests
import m3u8

def get_playlist_uris(video_id, access_token):
	"""
	Grabs the URI's for accessing each of the video chunks.
	"""
	url = f"http://usher.twitch.tv/vod/{video_id}"

	resp = requests.get(url, params={
		"nauth": access_token['value'],
		"nauthsig": access_token['signature'],
		"allow_source": "true",
		"player": "twitchweb",
	})
	resp.raise_for_status()

	data = resp.content.decode("utf-8")

	playlist = m3u8.loads(data)
	playlist_uris = []

	for p in playlist.playlists:
		playlist_uris += [p.uri]
	
	return playlist_uris

def dl_video(video_id, path):
	# Grab access token
	access_token = gql.get_access_token(video_id)
	# Get M3U8 playlist, and parse them
	# (first URI is always source quality!)
	uris = get_playlist_uris(video_id, access_token)
	print(uris)
	# Create a temp dir in .vodbot/temp
	# Download VOD chunks to the temp folder
	# join the vods using ffmpeg at specified path
	# delete temp folder and contents
	pass

def dl_clip(id, path):
	# Grab full video identifier
	# Get proper clip file URL
	# download file to path
	pass
   