# Dedicated module for the config class and associated classes
# having a dedicated type makes accessing specific members easier and dictated

from typing import Dict, List, Literal, Tuple
from pathlib import Path

# class ChannelThumbnailIcon:
# 	def __init__(self, path:str, ox:int, oy:int) -> None:
# 		self.path = path
# 		self.ox = ox
# 		self.oy = oy

class _ConfigChannel:
	def __init__(self,
		username:str="",
		save_vods:bool=True, save_clips:bool=True, save_chat:bool=True,
	**kwargs) -> None:
		self.username = username
		
		self.save_vods = save_vods
		self.save_clips = save_clips
		self.save_chat = save_chat

class _ConfigPull:
	def __init__(self,
		save_chat:bool=True, gql_client:str="kimne78kx3ncx6brgo4mv6wki5h1ko",
	**kwargs) -> None:
		# determines if chat logs get pulled with VODs and saved alongside metadata.
		# is a master switch for every channel, if false then no chat gets saved.
		self.save_chat = save_chat

		# Client ID for accessing Twitch's public facing but privately documented GraphQL interface.
		# The default argument in this function is the default client ID for a user not logged in,
		# and thus flies under the radar most of the time but does not allow accessing certain
		# amenities such as deleted chat messages from videos or private information about certain
		# accounts. Changing this to an ID associated with an account may result in a ban.
		self.gql_client = gql_client

		# Below is some flags and info for using the official V5 API over the private GQL API where
		# possible. Currently not implemented in any form and does not affect anything. This would
		# not allow for downloading VODs under an authorized Client ID, or any sort of undocumented
		# or nonexistant API access, still requiring GQL access in these cases.
		# TODO?
		#self.api_use_alt = False
		#self.api_client = ""
		#self.api_secret = ""

class _ConfigChat():
	def __init__(self,
		export_format:Literal["raw","RealText","SAMI","YTT"]="RealText",
		message_display_time:int=10, randomize_uncolored_names:bool=True,
	**kwargs) -> None:
		# Dictates what closed caption format the chat logs should be exported to when exporting.
		self.export_format = export_format
		# Dictates how long a single message should appear in the closed caption export.
		self.message_display_time = message_display_time
		# Toggle for giving white names (uncolored) a random color.
		self.randomize_uncolored_names = randomize_uncolored_names

		# YouTube Timed Text formatting options TODO
		self.ytt_align = "left"
		self.ytt_position_weight = 6
		self.ytt_position_x = 0
		self.ytt_position_y = 100

class _ConfigStage():
	def __init__(self,
		description_macros:Dict[str, str]={}, timezone:str="+0000",
	**kwargs) -> None:
		# A UTC timezone code string, like "+0000" (GMT), "-0500" (EDT) or "+0930" (ACST). Used for
		# calculating certain dates relating to videos (which store their date as ISO 8601).
		self.timezone = timezone

		# A dictionary of keys and related strings to make typing descriptions for stages easier,
		# such as adding a lot of social media links at the end of a YouTube description.
		self.description_macros = description_macros

class _ConfigExport():
	def __init__(self,
		ffmpeg_loglevel:Literal["warning","error","fatal"]="warning",
		chat_enable:bool=True, video_enable:bool=True,
	**kwargs) -> None:
		# This is used to describe to FFMPEG what type of output there should be regarding when
		# the program directs it to manage video files. "warning" is recommended as it displays very
		# little unless otherwise necessary.
		self.ffmpeg_loglevel = ffmpeg_loglevel

		# A simple toggle for managing whether chat is exported with a stage, if available. More
		# options are available in the chat config section.
		self.chat_enable = chat_enable

		# A simple toggle for managing whether video is exported with a stage. Useful for if you
		# just need the chat logs.
		self.video_enable = video_enable

		# Hardware acceleration options
		# TODO?

class _ConfigUpload():
	def __init__(self,
		client_path:str=None, session_path:str=None, chat_enable:bool=True,
	**kwargs) -> None:
		# JSON files that contain important information relating to interfacing with YouTube.
		self.client_path = client_path # Must exist for functionality
		self.session_path = session_path # Must be accessible

		# A simple toggle for managing whether chat is uploaded with a video, if available. More
		# options are available in the chat config section. Only uploads YouTube Timed Text format.
		self.chat_enable = chat_enable

# class _ConfigThumbnailIcon():
# 	def __init__(self,
# 		offset_x:int=0, offset_y:int=0,
# 		scale:int=1, filepath:str="",
# 	**kwargs) -> None:
# 		self.offset_x = offset_x
# 		self.offset_y = offset_y
# 		self.scale = scale
# 		self.filepath = filepath

# class _ConfigThumbnail():
# 	def __init__(self,
# 		enable:bool=False,
# 		thumbnail_x:int=0, thumbnail_y:int=0,
# 		thumbnail_width:int=1280, thumbnail_height:int=720,
# 		thumbnail_filepath:str="",
# 		screenshot_x:int=0, screenshot_y:int=0,
# 		screenshot_width:int=1280, screenshot_height:int=720,
# 		text_font:str="", text_gravity:str="NorthWest", text_size:int=160,
# 		text_x:int=0, text_y:int=0,
# 		heads:Dict[str, _ConfigThumbnailIcon]=None, head_order:List[int]=None,
# 		head_positions:List[Tuple[int, int, int]]=None,
# 		games:Dict[str, _ConfigThumbnailIcon]=None,
# 		game_x:int=0,game_y:int=0,game_gravity:str="Center",
# 	**kwargs) -> None:
# 		pass # We'll do this later.

# class _ConfigWebhookBase():
# 	def __init__(self,
# 		enable:bool=True, display_name:str=None, webhook_url:str=None,
# 	**kwargs) -> None:
# 		self.enable = enable
# 		self.display_name = display_name
# 		self.webhook_url = webhook_url

# class _ConfigWebhooks():
# 	def __init__(self,
# 		enable:bool=False, display_name:str="VodBot", webhook_url:str="",
# 		pull_vod:_ConfigWebhookBase=None,
# 		pull_clip:_ConfigWebhookBase=None,
# 		pull_job_done:_ConfigWebhookBase=None,
# 		export_video:_ConfigWebhookBase=None,
# 		export_job_done:_ConfigWebhookBase=None,
# 		upload_video:_ConfigWebhookBase=None,
# 		upload_job_done:_ConfigWebhookBase=None,
# 	**kwargs) -> None:
# 		pass # We'll do this later.
# 		self.enable = enable
# 		self.display_name = display_name
# 		self.webhook_url = webhook_url

# 		self.pull_vod = pull_vod
# 		self.pull_clip = pull_clip
# 		self.pull_job_done = pull_job_done
# 		self.export_video = export_video
# 		self.export_job_done = export_job_done
# 		self.upload_video = upload_video
# 		self.upload_job_done = upload_job_done

class _ConfigDirectories():
	def __init__(self,
		vod:str, clip:str,
		temp:str, stage:str,
		thumbnail:str,
	**kwargs) -> None:
		# Each key relates to a specific directory. `vod` is for storing VOD files, with metadata
		# and chat (as applicable). `clip` is the same as the previous. Both are recommended to be
		# on slow, dense storage devices `temp` is a working directory where video data is sliced,
		# spliced, and processed, recommended to be on a high speed storage device. `stage` is a
		# directory for storing information about to-be-processed files. `thumbnail` is for storing
		# lots of images used for generating thumbnails for processed videos, it is the prefix to
		# the filepaths in the thumbnail config for heads and games.
		self.vod = Path(vod)
		self.clip = Path(clip)
		self.temp = Path(temp)
		self.stage = Path(stage)
		self.thumbnail = Path(thumbnail)

class Config:
	def __init__(self, conf:dict) -> None:
		self.channels = {} # channels to watch for new clips and videos
		_check_required_type(conf, "channels", dict)
		for name, settings in conf["channels"].items():
			_check_required_type(settings, "channel", str)
			_check_optional_type(settings, "save_chat", bool)
			_check_optional_type(settings, "save_vods", bool)
			_check_optional_type(settings, "save_clips", bool)
			self.channels[name] = _ConfigChannel(**settings)
		
		# is actually optional
		if _check_optional_type(conf, "pull", dict):
			pull = conf["pull"]
			_check_optional_type(pull, "save_chat", bool)
			_check_optional_type(pull, "gql_client_id", str)
			# _check_optional_type(pull, "api_use_alt", bool)
			# _check_optional_type(pull, "api_client", str)
			# _check_optional_type(pull, "api_secret", str)
			self.pull = _ConfigPull(**pull)
		else:
			self.pull = _ConfigPull()
		
		if _check_optional_type(conf, "chat", dict):
			chat = conf["chat"]
			_check_optional_type(chat, "export_format", bool)
			_check_optional_type(chat, "message_display_time", int)
			_check_optional_type(chat, "randomize_uncolored_names", bool)
			_check_optional_type(chat, "ytt_x", int)
			_check_optional_type(chat, "ytt_y", int)
			_check_optional_type(chat, "ytt_align", str)
			_check_optional_type(chat, "ytt_weight", int)
			self.pull = _ConfigChat(**chat)
		else:
			self.chat = _ConfigChat()

		if _check_optional_type(conf, "stage", dict):
			stage = conf["stage"]
			# check each key to actually be a string
			if _check_optional_type(stage, "description_macros", dict):
				desc_macros = stage["description_macros"]
				for key in desc_macros:
					_check_required_type(desc_macros, key, str)
			_check_optional_type(stage, "timezone", str)
			self.stage = _ConfigStage(**stage)
		else:
			self.stage = _ConfigStage()

		if _check_optional_type(conf, "export", dict):
			export = conf["export"]
			_check_optional_type(export, "ffmpeg_loglevel", str)
			_check_optional_type(export, "chat_enable", bool)
			_check_optional_type(export, "video_enable", bool)
			self.export = _ConfigExport(**export)
		else:
			self.export = _ConfigExport()


		if _check_optional_type(conf, "upload", dict):
			upload = conf["upload"]
			_check_optional_type(upload, "client_path", str)
			_check_optional_type(upload, "session_path", str)
			_check_optional_type(upload, "chat_enable", bool)
			self.upload = _ConfigUpload(**upload)
		else:
			self.upload = _ConfigUpload()

		#self.thumbnail = _ConfigThumbnail()
		#self.webhooks = _ConfigWebhooks()

		# Directories should maybe be optional?
		_check_required_type(conf, "directories", dict)
		directories = conf["directories"]
		_check_required_type(directories, "vods", str)
		_check_required_type(directories, "clips", str)
		_check_required_type(directories, "temp", str)
		_check_required_type(directories, "stage", str)
		_check_required_type(directories, "thumbnail", str)
		# validate paths here?
		self.directories = _ConfigDirectories(**directories)

# Errors if key does not exist or is not the correct type.
def _check_required_type(conf:dict, key:str, ttype:type):
	if key not in conf:
		pass # "required key value pair not in config, needed {key}."
	else:
		return _check_optional_type(conf, key, ttype)

# Errors if key is not the correct type, but not required to exist.
def _check_optional_type(conf:dict, key:str, ttype:type):
	if key in conf and not isinstance(conf[key], ttype):
		pass # "key does not match desired type of {ttype}, got {type(conf[key])}."

	return True
