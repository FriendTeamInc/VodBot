from pathlib import Path

from . import gql, worker
from vodbot import chatlog
from vodbot.util import make_dir, format_size
from vodbot.printer import cprint
from vodbot.twitch import Vod, Clip, get_video_comments
from vodbot.config import Config

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
	url = f"http://usher.ttvnw.net/vod/{video_id}"

	resp = requests.get(url, timeout=5, params={
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

def dl_video(conf: Config, video: Vod, path: str):
	TEMP_DIR = conf.directories.temp
	LOG_LEVEL = conf.export.ffmpeg_loglevel
	REDIRECT = conf.export.ffmpeg_stderr

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
	path_map = worker.download_files(conf, video_id, base_uri, tempdir, vod_paths)
	# cprint("\t#dDone, now to FFmpeg join...#r")

	# join the vods using FFmpeg at specified path
	cwd = os.getcwd()
	os.chdir(str(tempdir))
	cmd = [
		"ffmpeg", "-allowed_extensions", "ALL",
		"-i", str(playlist_path),
		"-c", "copy", path, "-y",
		"-stats", "-loglevel", LOG_LEVEL
	]
	redirect = subprocess.DEVNULL
	if REDIRECT != Path():
		redirect = open(REDIRECT, "w")
	result = subprocess.run(cmd, stderr=redirect)
	if REDIRECT != Path():
		redirect.close()
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


def dl_clip(conf: Config, clip: Clip, path: str):
	clip_slug = clip.slug
	clip_id = clip.id

	# Get proper clip file URL
	source_url = gql.get_clip_source(clip_slug)

	# Download file to path
	size, _ = worker.download_file(source_url, path, conf.pull.connection_retries, conf.pull.connection_timeout, conf.pull.chunk_size)

	# Print progress
	cprint(f"#fM#lClip#r `#fM{clip_slug}#r` ({clip_id}) #fB#l{format_size(size)}#r")
