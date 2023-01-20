from pathlib import Path

from . import gql, worker
from vodbot import chatlog
from vodbot.util import make_dir, format_size
from vodbot.printer import cprint
from vodbot.twitch import Vod, Clip, get_video_comments

import subprocess
import requests
import shutil
import m3u8
import os

class JoiningFailed(Exception):
	pass

def get_playlist_uris(video_id: str, access_token: dict):
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
	playlist_uris = [p.uri for p in playlist.playlists]
	
	return playlist_uris

def dl_video(video: Vod, TEMP_DIR: Path, path: str, max_workers: int, LOG_LEVEL: str, REDIRECT: Path):
	video_id = video.id

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
	tempdir = TEMP_DIR / video_id
	make_dir(str(tempdir))

	# Dump playlist to a file
	playlist_path = tempdir / "playlist.m3u8"
	playlist.dump(str(playlist_path))

	# Get all the necessary vod paths for the uri
	base_uri = "/".join(source_uri.split("/")[:-1]) + "/"
	vod_paths = [segment.uri for segment in playlist.segments]
	
	# Download VOD chunks to the temp folder
	path_map = worker.download_files(video_id, base_uri, tempdir, vod_paths, max_workers)
	# TODO: rewrite this output to look nicer and remove FFmpeg output using COLOR_CODES["F"]
	cprint("#dDone, now to FFmpeg join...#r")

	# join the vods using FFmpeg at specified path
	# TODO: change this to the concat function in video?
	cwd = os.getcwd()
	os.chdir(str(tempdir))
	cmd = [
		"ffmpeg", "-i", str(playlist_path),
		"-c", "copy", path, "-y",
		"-stats", "-loglevel", LOG_LEVEL
	]
	redirect = subprocess.DEVNULL
	if REDIRECT != Path():
		redirect = REDIRECT
	result = subprocess.run(cmd, stderr=redirect, check=True)
	os.chdir(cwd)

	if result.returncode != 0:
		raise JoiningFailed()

	# delete temp folder and contents
	shutil.rmtree(str(tempdir))


def dl_video_chat(video: Vod, path: str):
	video_id = video.id

	# Download all chat from video
	cprint(f"#fM#lVOD Chat#r `#fM{video_id}#r` (0%)", end="")
	msgs = get_video_comments(video_id)
	cprint(f"\r#fM#lVOD Chat#r `#fM{video_id}#r` (100%); Done, now to write...", end="")

	chatlog.chat_to_logfile(msgs, path)

	cprint(f"\r#fM#lVOD Chat#r `#fM{video_id}#r` (100%); Done, now to write... Done")


def dl_clip(clip: Clip, path: str):
	clip_slug = clip.slug
	clip_id = clip.id

	# Get proper clip file URL
	source_url = gql.get_clip_source(clip_slug)

	# Download file to path
	size, _existed = worker.download_file(source_url, path)

	# Print progress
	cprint(f"#fM#lClip#r `#fM{clip_slug}#r` ({clip_id}) #fB#l{format_size(size)}#r")