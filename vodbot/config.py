# Dedicated module for the config class and associated classes
# having a dedicated type makes accessing specific members easier and dictated

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, List, Literal, Tuple
from pathlib import Path


@dataclass_json
@dataclass
class _ConfigChannel:
	username: str
	save_vods: bool
	save_clips: bool
	save_chat: bool

@dataclass_json
@dataclass
class _ConfigPull:
	# Determines if chat logs get pulled with VODs and saved alongside metadata. This is a master
	# switch for every channel, if false then no chat gets saved.
	save_chat: bool
	# Client ID for accessing Twitch's public facing but privately documented GraphQL interface, 
	# which is significantly more advanced than the V5 API. Do not change this to a specific user's
	# ID unless you want to risk a ban, although it allows for accessing private info such as
	# deleted chat messages and account info.
	gql_client: str = "kimne78kx3ncx6brgo4mv6wki5h1ko"

	# Below is some flags and info for using the official V5 API over the private GQL API where
	# possible. Currently not implemented in any form and does not affect anything. This would
	# not allow for downloading VODs under an authorized Client ID, or any sort of undocumented
	# or nonexistant API access, still requiring GQL access in these cases.
	# TODO?
	#api_use_alt: bool = False
	#api_client: str = ""
	#api_secret: str = ""
	pass

@dataclass_json
@dataclass
class _ConfigChat():
	# Dictates what closed caption format the chat logs should be exported to when exporting. This
	# is ignored when uploading as uploading to YouTube will always use the YTT format.
	export_format: Literal["raw","RealText","SAMI","YTT"] = "YTT"
	# Dictates how long a single message should appear in the closed caption export.
	message_display_time: int = 10
	# Toggle for giving white names (uncolored) a random color.
	randomize_uncolored_names: bool = True
	
	# YouTube Timed Text formatting options TODO
	ytt_align: str = "left"
	ytt_position_weight: int = 6
	ytt_position_x: int = 0
	ytt_position_y: int = 100

@dataclass_json
@dataclass
class _ConfigStage():
	# A UTC timezone code string, like "+0000" (GMT), "-0500" (EDT) or "+0930" (ACST). Used for
	# calculating certain dates relating to videos (which store their date as ISO 8601).
	timezone: str = "+0000"
	# A dictionary of keys and related strings to make typing descriptions for stages easier,
	# such as adding a lot of social media links at the end of a YouTube description.
	description_macros: Dict[str, str] = {}

@dataclass_json
@dataclass
class _ConfigExport():
	# This is used to describe to FFMPEG what type of output there should be regarding when
	# the program directs it to manage video files. "warning" is recommended as it displays very
	# little unless otherwise necessary.
	ffmpeg_loglevel: Literal["warning", "error", "fatal"] = "warning"
	# A simple toggle for managing whether chat is exported with a stage, if available. More
	# options are available in the chat config section.
	chat_enable: bool = True
	# A simple toggle for managing whether video is exported with a stage. Useful for if you
	# just need the chat logs.
	video_enable: bool = True
	# Hardware acceleration options
	# TODO?
	pass

@dataclass_json
@dataclass
class _ConfigUpload():
	client_path: Path
	session_path: Path
	chat_enable: bool

@dataclass_json
@dataclass
class _ConfigThumbnailIcon():
	offset_x: int
	offset_y: int
	scale: int
	filepath: Path

@dataclass_json
@dataclass
class _ConfigThumbnail():
	enable: bool
	thumbnail_x: int; thumbnail_y: int
	thumbnail_width: int; thumbnail_height: int
	thumbnail_filepath: Path
	screenshot_x: int; screenshot_y: int
	screenshot_width: int; screenshot_height: int
	text_x: int; text_y: int
	text_font: str; text_size: int; text_gravity: str
	heads: Dict[str, _ConfigThumbnailIcon]
	head_order: List[int]
	head_positions: List[Tuple[int, int, int]]
	games: dict[str, _ConfigThumbnailIcon]
	game_x: int; game_y: int; game_gravity: str

@dataclass_json
@dataclass
class _ConfigWebhookBase():
	enable: bool
	display_name: str
	webhook_url: str

@dataclass_json
@dataclass
class _ConfigWebhooks():
	enable: bool
	display_name: str
	webhook_url: str
	pull_vod: _ConfigWebhookBase
	pull_clip: _ConfigWebhookBase
	pull_job_done: _ConfigWebhookBase
	export_video: _ConfigWebhookBase
	export_job_done: _ConfigWebhookBase
	upload_video: _ConfigWebhookBase
	upload_job_done: _ConfigWebhookBase

@dataclass_json
@dataclass
class _ConfigDirectories():
	# Each key relates to a specific directory. 
	# - `vod` is for storing VOD files, with metadata and chat (as applicable).
	# - `clip` is the same as the previous. Both are recommended to be on dense storage devices.
	# - `temp` is a working directory where video data is sliced, spliced, and processed,
	# recommended to be on a high speed storage device.
	# - `stage` is a directory for storing information about to-be-processed video files.
	# - `thumbnail` is for storing lots of images used for generating thumbnails for processed
	# videos, it is the prefix to the filepaths in the thumbnail config for heads and games.
	vod: Path
	clip: Path
	temp: Path
	stage: Path
	thumbnail: Path

@dataclass_json
@dataclass
class Config:
	channels: Dict[str, _ConfigChannel]
	pull: _ConfigPull
	chat: _ConfigChat
	stage: _ConfigStage
	export: _ConfigExport
	upload: _ConfigUpload
	# thumbnail: _ConfigThumbnail
	# webhooks: _ConfigWebhooks
	directories: _ConfigDirectories
