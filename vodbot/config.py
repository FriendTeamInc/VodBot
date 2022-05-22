# Dedicated module for the config class and associated classes
# having a dedicated type makes accessing specific members easier and dictated

from cgitb import enable
from typing import Dict, List, Literal, Tuple
from pathlib import Path

# class ChannelThumbnailIcon:
# 	def __init__(self, path:str, ox:int, oy:int) -> None:
# 		self.path = path
# 		self.ox = ox
# 		self.oy = oy

class _ConfigChannel:
	def __init__(self,
		name:str, username:str,
		save_vods:bool=True, save_clips:bool=True, save_chat:bool=True,
		# thumbnail_icon:ConfigChannelThumbnailIcon=None
	) -> None:
		self.name = name
		self.username = username
		
		self.save_vods = save_vods
		self.save_clips = save_clips
		self.save_chat = save_chat

		# self.thumbnail_icon = thumbnail_icon

class _ConfigPull:
	def __init__(self,
		save_chat:bool=True,
		gql_client:str="kimne78kx3ncx6brgo4mv6wki5h1ko"
	) -> None:
		# determines if chat logs get pulled with VODs and saved alongside metadata.
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
		message_display_time:int=10,
		randomize_uncolored_names:bool=True,
	) -> None:
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
		description_macros:Dict[str, str]={},
		timezone:str="+0000"
	) -> None:
		# A UTC timezone code string, like "+0000" (GMT), "-0500" (EDT) or "+0930" (ACST). Used for
		# calculating certain dates relating to videos (which store their date as ISO 8601).
		self.timezone = timezone

		# A dictionary of keys and related strings to make typing descriptions for stages easier,
		# such as adding a lot of social media links at the end of a YouTube description.
		self.description_macros = description_macros

class _ConfigExport():
	def __init__(self,
		ffmpeg_loglevel:Literal["warning","error","fatal"]="warning",
		chat_enable:bool=True
	) -> None:
		# This is used to describe to FFMPEG what type of output there should be regarding when
		# the program directs it to manage video files. "warning" is recommended as it displays very
		# little unless otherwise necessary.
		self.ffmpeg_loglevel = ffmpeg_loglevel

		# A simple toggle for managing whether chat is exported with a video, if available. More
		# options are available in the chat config section.
		self.chat_enable = chat_enable

		# Hardware acceleration options
		# TODO?

class _ConfigUpload():
	def __init__(self,
		client_path:str, credentials_path:str,
		chat_enable:bool=True
	) -> None:
		# JSON files that contain important information relating to interfacing with YouTube.
		self.client_path = client_path
		self.credentials_path = credentials_path

		# A simple toggle for managing whether chat is uploaded with a video, if available. More
		# options are available in the chat config section. Only uploads YouTube Timed Text format.
		self.chat_enable = chat_enable

class _ConfigThumbnailHead():
	pass

class _ConfigThumbnailGame():
	pass

class _ConfigThumbnail():
	def __init__(self,
		enable:bool=False,
		thumbnail_x:int=0, thumbnail_y:int=0,
		thumbnail_width:int=1280, thumbnail_height:int=720,
		thumbnail_path:str="",
		screenshot_x:int=0, screenshot_y:int=0,
		screenshot_width:int=1280, screenshot_height:int=720,
		font:str="", font_gravity:str="NorthWest", font_size:int=160,
		font_x:int=0,font_y:int=0,
		heads:List[_ConfigThumbnailHead]=None,
		head_order:List[int]=None,
		head_positions:List[Tuple[int,int]]=None,
		games:List[_ConfigThumbnailGame]=None,
		game_x:int=0,game_y:int=0,game_weight:str="Center"
	) -> None:
		pass

class _ConfigWebhookBase():
	def __init__(self,
		enable:bool=False, display_name:str="VodBot",
		webhook_url:str="", avatar_url:str=""
	) -> None:
		self.enable = enable
		self.display_name = display_name
		self.webhook_url = webhook_url
		self.avatar_url = avatar_url

class _ConfigWebhooks():
	def __init__(self,
		enable:bool=False, display_name:str="VodBot",
		webhook_url:str="", avatar_url:str="",
		pull_vod:_ConfigWebhookBase=None,
		pull_clip:_ConfigWebhookBase=None,
		pull_job_done:_ConfigWebhookBase=None,
		export_video:_ConfigWebhookBase=None,
		export_job_done:_ConfigWebhookBase=None,
		upload_video:_ConfigWebhookBase=None,
		upload_job_done:_ConfigWebhookBase=None,
	) -> None:
		self.enable = enable
		self.display_name = display_name
		self.webhook_url = webhook_url
		self.avatar_url = avatar_url

		self.pull_vod = pull_vod
		self.pull_clip = pull_clip
		self.pull_job_done = pull_job_done
		self.export_video = export_video
		self.export_job_done = export_job_done
		self.upload_video = upload_video
		self.upload_job_done = upload_job_done

class _ConfigDirectories():
	def __init__(self,
		vod:str, clip:str,
		temp:str, stage:str,
		thumbnail:str
	) -> None:
		# Each key relates to a specific directory. `vod` is for storing VOD files, with metadata
		# and chat (as applicable). `clip` is the same as the previous. Both are recommended to be
		# on slow, dense storage devices `temp` is a working directory where video data is sliced,
		# spliced, and processed, recommended to be on a high speed storage device. `stage` is a
		# directory for storing information about to-be-processed files. `thumbnail` is for storing
		# lots of images used for generating thumbnails for processed videos.
		self.vod = Path(vod)
		self.clip = Path(clip)
		self.temp = Path(temp)
		self.stage = Path(stage)
		self.thumbnail = Path(thumbnail)

class Config:
	def __init__(self, **kwargs) -> None:
		self.channels = [] # channels to watch for new clips and videos
		self.pull = _ConfigPull()
		self.stage = _ConfigStage()
		self.export = _ConfigExport()
		self.upload = _ConfigUpload()
		self.thumbnail = _ConfigThumbnail()
		self.webhooks = _ConfigWebhooks()
		self.directories = _ConfigDirectories()
	
	def load_json() -> None:
		pass
