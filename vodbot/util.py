# Module to pull and create different files and directories on the OS

from .printer import cprint

import os
import sys
import json
from pathlib import Path
from collections import OrderedDict


vodbotdir = Path.home() / ".vodbot"
DEFAULT_CONF_PATH = vodbotdir / "conf.json"

class ConfigChannelThumbnailIcon:
	def __init__(self, path:str, ox:int, oy:int) -> None:
		self.path = path
		self.ox = ox
		self.oy = oy
		pass

class ConfigChannel:
	def __init__(self,
		name:str, username:str,
		save_vods:bool=True, save_clips:bool=True, save_chat:bool=True,
		thumbnail_icon:ConfigChannelThumbnailIcon=None
	) -> None:
		self.name = name
		self.username = username
		
		self.save_vods = save_vods
		self.save_clips = save_clips
		self.save_chat = save_chat

		self.thumbnail_icon = thumbnail_icon

class ConfigPull:
	def __init__(self) -> None:
		pass

class ConfigStage:
	def __init__(self) -> None:
		pass

class ConfigExport:
	def __init__(self) -> None:
		pass

class ConfigUpload:
	def __init__(self) -> None:
		pass

class ConfigThumbnail:
	def __init__(self) -> None:
		pass

class ConfigThumbnails:
	def __init__(self) -> None:
		pass

class ConfigWebhooks:
	def __init__(self) -> None:
		pass

class ConfigDirectories:
	def __init__(self, vods:str, clips:str, temp:str, stage:str, thumbnails:str) -> None:
		self.vods = vods
		self.clips = clips
		self.temp = temp
		self.stage = stage
		self.thumbnails = thumbnails

class Config:
	def __init__(self) -> None:
		self.channels = []
		self.pull = OrderedDict([
			("save_chat", True),
			("gql_client", "kimne78kx3ncx6brgo4mv6wki5h1ko"),
			("api_use_alt", False),
			("api_client", ""),
			("api_secret", "")
		])
		self.stage = OrderedDict([
			("timezone", "+0000"),
			("description_macros", OrderedDict([
				("captions", "Want to read chat? Enable Closed Captioning!"),
				("watch", "Watch streams live at {links}"),
				("discord", "Join the FTI Discord: https://discord.gg/v2t6uag"),
				("vodbot", "Stream archived by VodBot: https://github.com/NotQuiteApex/VodBot"),
				("end", "on {date}\n\n{captions}\n{watch}\n{discord}\n{vodbot}")
			]))
		])
		self.export = OrderedDict([
			("ffmpeg_loglevel", "warning"),

			("hardware_accel", OrderedDict([
				("enable", False),
				("hw_args", "")
			]))

			("chat", OrderedDict([
				("enable", True),
				("msg_time", 10),
				("format", "RealText"),
				("randomize_uncolored_names", True),
			]))
		])
		self.upload = OrderedDict([
			("client_path", str(vodbotdir / "yt-client.json")),
			("pickle_path", str(vodbotdir / "yt-session.pkl")),

			("chat_export", OrderedDict([
				("enable", True),
				("msg_time", 10),
				("randomize_uncolored_names", True),

				("format", OrderedDict([
					("align", "left"), ("pos_weight", 6),
					("pos_x", 0), ("pos_y", 100),
				]))
			]))
		])
		self.thumbnail = OrderedDict([
			("enable", False),

			("thumb_size", "1280x720"),
			("thumb_x", 0), ("thumb_y", 0),
			("thumb_w,h", "1280,720"),
			("thumb_path", "thumb_bg.png"),

			("screenshot_x", 300), ("screenshot_y", 0),
			("screenshot_w,h", "1280,720"),

			("font", "Ubuntu-Bold-Italic"),
			("font_size", 160), ("font_x", 420), ("font_y", 50),
			("font_gravity", "NorthWest"),

			("head_order", [5,6,7,8,4,3,2,1]),
			("head_positions", [
				[250, 250], [465, 280],
				[100, 388], [502, 508], [250, 250, 2],
				[130, 616], [544, 650], [342, 654],
			]),

			("game_x", -430), ("game_y", -240),
			("game_gravity", "Center"), ("games", [])
		])
		self.webhooks = OrderedDict([
			("enable", False),
			("name", "VodBot"),
			("webhook_url", ""),
			("avatar_url", ""),

			("pull_vod", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),
			("pull_clip", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),
			("pull_job_done", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),

			("export_video", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),
			("export_job_done", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),

			("upload_video", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),
			("upload_job_done", OrderedDict([ ("enable", False), ("name", ""), ("webhook_url", ""), ("avatar_url", ""), ("msg", "") ])),
		])
		self.directories = OrderedDict([
			("vod", str(vodbotdir / "vods")),
			("clip", str(vodbotdir / "clips")),
			("temp", str(vodbotdir / "temp")),
			("stage", str(vodbotdir / "stage")),
			("thumbnail", str(vodbotdir / "thumbnail")),
		])

	def load_json(j) -> None:

		pass

DEFAULT_CONF = OrderedDict([
	("twitch_channels", []), # channels to watch for new clips and videos

	("pull_chat_logs", True), # determines if chat logs get pulled with VODs

	("stage_timezone", "+0000"), # timezone for when a video happened
	("stage_format", { # Macros for video descriptions when staging
		"watch": "-- Watch live at {links}",
		"discord": "-- Join the Discord at https://discord.gg/v2t6uag",
		"credits": "\n{watch}\n{discord}"
	}),
	("stage_upload_delete", True), # delete a stage on completed upload?
	("stage_export_delete", True), # delete a stage on completed export?

	("chat_msg_time", 10), # measured in seconds, how long to show a chat message in subtitle
	("chat_upload", "YTT"), # can be RealText, YTT, or SAMI
	("chat_export", "raw"), # can be raw, RealText, YTT, or SAMI

	("ffmpeg_loglevel", "warning"), # warning (recommended), error (only breaking stuff), fatal (absolute error)
	
	("youtube_client_path", str(vodbotdir / "yt-client.json")), # google generated json for using youtube api
	("youtube_pickle_path", str(vodbotdir / "yt-session.pkl")), # caching oauth session and info
	
	("vod_dir", str(vodbotdir / "vods")), # place to store video data
	("clip_dir", str(vodbotdir / "clips")), # clip data
	("temp_dir", str(vodbotdir / "temp")), # temp data
	("stage_dir", str(vodbotdir / "stage")) # stage data
])


def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A string of where the directory structure should be made.
	"""
	os.makedirs(str(directory), exist_ok=True)


def load_conf(filename):
	"""
	Loads the config of VodBot at a specific directory.

	:param filename: File name of the JSON formatted configuration file.
	:returns: Dictionary created from the conf file.
	"""

	conf = None
	try:
		with open(filename) as f:
			conf = json.load(f)
	except FileNotFoundError:
		exit_prog(2, f"Config not found. You can configure VodBot with the init command.")
	except json.decoder.JSONDecodeError as e:
		exit_prog(98, f"Failed to decode config. \"{e.msg}\"")
		
	for key in DEFAULT_CONF:
		if key not in conf:
			exit_prog(79, f"Missing key \"{key}\" in config, please edit your config to continue.")
	
	if conf["youtube_client_path"] == "":
		cprint("Please edit your config with your Youtube Client ID and Secret to use the upload command.")

	if len(conf["twitch_channels"]) == 0:
		exit_prog(40, "No channels listed in config, please edit your config to continue.")

	chat_format = ["RealText", "SAMI", "YTT"]
	if conf["chat_upload"] not in chat_format:
		exit_prog(10, f"Chat format for uploading not valid. Got `{conf['chat_upload']}`, expected any of the following `{chat_format}`. Fix your config to continue.")
	chat_format.append("raw")
	if conf["chat_export"] not in chat_format:
		exit_prog(10, f"Chat format for exporting not valid. Got `{conf['chat_export']}`, expected any of the following `{chat_format}`. Fix your config to continue.")
	
	# TODO: Check all important config options

	return conf


def exit_prog(code=0, errmsg=None):
	"""
	Exits the program with an error code and optional error message.

	:param code: The error code to exit with. Should be unique per exit case.
	:param errmsg: The corresponding error message to print when exiting.
	"""

	print()

	if code != 0:
		msg = f"#r#fR#lERROR! #fY#l({code})#r"
		if errmsg != None:
			msg += " #fR#l" + errmsg + "#r"
		cprint(msg, end=" ")

	cprint("#r#dExiting...#r")
	sys.exit(code)
