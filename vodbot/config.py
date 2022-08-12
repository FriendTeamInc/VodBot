# Dedicated module for the config class and associated classes
# having a dedicated type makes accessing specific members easier and dictated

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from marshmallow import fields, validate, ValidationError
from typing import Dict, List, Tuple, Any, Mapping
from pathlib import Path


DEFAULT_CONFIG_DIRECTORY = Path.home() / ".vodbot"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIRECTORY / "config.json"


class _MMPath(fields.Field):
	def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
		return str(value)
	
	def _deserialize(self, value: Any, attr: str | None, data: Mapping[str, Any] | None, **kwargs):
		try:
			return Path(value)
		except (ValueError, TypeError) as e:
			raise ValidationError("Must be a valid file/directory path string.") from e

_path_field_config = config(encoder=lambda x: str(x), decoder=lambda x: Path(x), mm_field=_MMPath())


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
	save_chat: bool = True
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

@dataclass_json
@dataclass
class _ConfigChat:
	# Dictates what closed caption format the chat logs should be exported to when exporting. This
	# is ignored when uploading as uploading to YouTube will always use the YTT format.
	export_format: str = field(default="YTT", metadata=config(mm_field=fields.Str(
		validate=validate.OneOf(["raw","RealText","SAMI","YTT"]))))
	# Dictates how long a single message should appear in the closed caption export.
	message_display_time: int = 10
	# Toggle for giving white names (uncolored) a random color.
	randomize_uncolored_names: bool = True
	
	# YouTube Timed Text formatting options TODO
	ytt_align: str = field(default="left", metadata=config(mm_field=fields.Str(
		validate=validate.OneOf(["left", "right", "center"]))))
	ytt_anchor: int = field(default=6, metadata=config(mm_field=fields.Int(
		validate=validate.Range(0, 8))))
	ytt_position_x: int = field(default=0, metadata=config(mm_field=fields.Int(
		validate=validate.Range(0, 100))))
	ytt_position_y: int = field(default=100, metadata=config(mm_field=fields.Int(
		validate=validate.Range(0, 100))))

@dataclass_json
@dataclass
class _ConfigStage:
	# A UTC timezone code string, like "+0000" (GMT), "-0500" (EDT) or "+0930" (ACST). Used for
	# calculating certain dates relating to videos (which store their date as ISO 8601).
	timezone: str = field(default_factory=lambda: "+0000")
	# A dictionary of keys and related strings to make typing descriptions for stages easier,
	# such as adding a lot of social media links at the end of a YouTube description.
	description_macros: Dict[str, str] = field(default_factory=lambda: {})

@dataclass_json
@dataclass
class _ConfigExport:
	# This is used to describe to FFMPEG what type of output there should be regarding when
	# the program directs it to manage video files. "warning" is recommended as it displays very
	# little unless otherwise necessary.
	ffmpeg_loglevel: str = field(default="warning", metadata=config(mm_field=fields.Str(
		validate=validate.OneOf(["warning", "error", "fatal"]))))
	# A simple toggle for managing whether chat is exported with a stage, if available. More
	# options are available in the chat config section.
	chat_enable: bool = True
	# A simple toggle for managing whether video is exported with a stage. Useful for if you
	# just need the chat logs.
	video_enable: bool = True
	# Hardware acceleration options
	# TODO?

@dataclass_json
@dataclass
class _ConfigUpload:
	chat_enable: bool = True
	client_path: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"yt-client.json", metadata=_path_field_config)
	session_path: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"yt-session.json", metadata=_path_field_config)

@dataclass_json
@dataclass
class _ConfigThumbnailIcon:
	offset_x: int
	offset_y: int
	scale: int
	filepath: Path = field(metadata=_path_field_config)

@dataclass_json
@dataclass
class _ConfigThumbnail:
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
class _ConfigWebhookBase:
	enable: bool = None
	display_name: str = None
	webhook_url: str = None

@dataclass_json
@dataclass
class _ConfigWebhooks:
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
class _ConfigDirectories:
	# Each key relates to a specific directory. 
	# - `vods` is for storing VOD files, with metadata and chat (as applicable).
	# - `clips` is the same as the previous. Both are recommended to be on dense storage devices.
	# - `temp` is a working directory where video data is sliced, spliced, and processed,
	# recommended to be on a high speed storage device.
	# - `stage` is a directory for storing information about to-be-processed video files.
	# - `thumbnail` is for storing lots of images used for generating thumbnails for processed
	# videos, it is the prefix to the filepaths in the thumbnail config for heads and games.

	vods: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"vods", metadata=_path_field_config)
	clips: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"clips", metadata=_path_field_config)
	temp: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"temp", metadata=_path_field_config)
	stage: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"stage", metadata=_path_field_config)
	#thumbnail: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"thumbnail", metadata=_path_field_config)

@dataclass_json
@dataclass
class Config:
	# The master copy of the config, the default.
	channels: Dict[str, _ConfigChannel] = field(default_factory=lambda: {}) # TODO: validate channels dict?
	pull: _ConfigPull = field(default_factory=lambda: _ConfigPull())
	chat: _ConfigChat = field(default_factory=lambda: _ConfigChat())
	stage: _ConfigStage = field(default_factory=lambda: _ConfigStage())
	export: _ConfigExport = field(default_factory=lambda: _ConfigExport())
	upload: _ConfigUpload = field(default_factory=lambda: _ConfigUpload())
	# thumbnail: _ConfigThumbnail = field(default_factory=lambda: _ConfigThumbnail())
	# webhooks: _ConfigWebhooks = field(default_factory=lambda: _ConfigWebhooks())
	directories: _ConfigDirectories = field(default_factory=lambda: _ConfigDirectories())


DEFAULT_CONFIG = Config.schema().load({})
