from . import gql, worker
from vodbot.util import make_dir, vodbotdir

import subprocess
import requests
import m3u8
import re

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

def dl_video(video_id, path, max_workers):
	# Grab access token
	access_token = gql.get_access_token(video_id)

	# Get M3U8 playlist, and parse them
	# (first URI is always source quality!)
	uris = get_playlist_uris(video_id, access_token)
	source_uri = uris[0]

	# Fetch playlist at proper quality
	resp = requests.get(source_uri)
	resp.raise_for_status()
	playlist = m3u8.loads(resp.text)

	# Create a temp dir in .vodbot/temp
	tempdir = vodbotdir / "temp" / video_id
	make_dir(str(tempdir))

	# Dump playlist to a file
	playlist_path = tempdir / "playlist.m3u8"
	playlist.dump(str(playlist_path))

	# Get all the necessary vod paths for the uri
	base_uri = re.sub("/[^/]+$", "/", source_uri)
	vod_paths = []
	for segment in playlist.segments:
		if segment.uri not in vod_paths:
			vod_paths.append(segment.uri)

	# Download VOD chunks to the temp folder
	path_map = worker.download_files(video_id, base_uri, tempdir, vod_paths, max_workers)
	print("Done, now to join...")

	# join the vods using ffmpeg at specified path
	cmd = [
		"ffmpeg", "-i", str(playlist_path),
		"-c", "copy", path, "-y",
		"-stats", "-loglevel", "warning"
	]

	result = subprocess.run(cmd)
	if result != 0:
		print("VOD joining failed! Preserving files...")
		return

	# delete temp folder and contents
	

def dl_clip(id, path, max_workers):
	# Grab full video identifier
	# Get proper clip file URL
	# download file to path
	pass
   