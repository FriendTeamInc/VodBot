# Dedicated module for the config class and associated classes
# having a dedicated type makes accessing specific members easier and dictated

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from marshmallow import fields, validate, ValidationError
from typing import Dict, List, Any, Mapping
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
	# Twitch username of the channel to pull (publicly available) data from.
	username: str = field(metadata=config(mm_field=fields.Str(
		validate=validate.Length(4, 25))))
	# Toggle for saving VOD videos.
	save_vods: bool = True
	# Toggle for saving Clip videos.
	save_clips: bool = True
	# Toggle for saving chat logs from VOD videos.
	save_chat: bool = True

@dataclass_json
@dataclass
class _ConfigPull:
	# Determines if VODs get pulled. Metadata will be saved if chatlogs are saved. This is a master
	# switch for every channel, if false then no VODs get saved.
	save_vods: bool = True
	# Determines if Clips get pulled. This is a master switch for every channel, if false then no
	# Clips get saved.
	save_clips: bool = True
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
		validate=validate.OneOf(["raw", "YTT"])))) # ["raw", "RealText", "SAMI", "YTT"]
	# Dictates how long a single message should appear in the closed caption export.
	message_display_time: int = 10
	# Toggle for giving white names (uncolored) a random color.
	randomize_uncolored_names: bool = True
	
	# TODO: YouTube Timed Text formatting options.
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
	# Toggle for deleting stage data on successful export.
	delete_on_export: bool = True
	# Toggle for deleting stage data on successful upload.
	delete_on_upload: bool = True

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
	# A simple toggle for managing whether a thumbnail is generated with a stage.
	thumbnail_enable: bool = True
	# TODO: Hardware acceleration options

@dataclass_json
@dataclass
class _ConfigUpload:
	# Toggle for uploading chat logs as closed captions.
	chat_enable: bool = True
	# Toggle for uploading generated thumbnails with the videos.
	thumbnail_enable: bool = True
	# Path for client JSON, the credentials needed for using the YouTube API.
	client_path: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"yt-client.json", metadata=_path_field_config)
	# Path for session JSON, the "cookies" for the logged-in YouTube account to upload videos to.
	session_path: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"yt-session.json", metadata=_path_field_config)
	# Size of chunks of uploaded data in bytes, with a minimum of 262144. It's recommended that this
	# size be a multiple of this minimum value.
	chunk_size: int = field(default=262144, metadata=config(mm_field=fields.Int(validate=validate.Range(262144))))

@dataclass_json
@dataclass
class _ConfigThumbnailIcon:
	# Offset/origin position of the image.
	ox: int
	oy: int
	# Path to an image. This path is always relative to the thumbnail directory.
	filepath: Path = field(metadata=_path_field_config)
	# Scale of the image, for when it is put into an image. It is scaled away from the offset point.
	# This is multiplied by the position's configured scale below.
	s: int = 1

@dataclass_json
@dataclass
class _ConfigThumbnailPosition:
	# Position for an image to be placed.
	x: int = 0
	y: int = 0
	# Offset/origin position of the image.
	ox: int = 0
	oy: int = 0
	# Scale of the image that will be placed at this point. It is scaled away from the offset point.
	# This is multiplied by the icon's configured scale above.
	s: int = 1

@dataclass_json
@dataclass
class _ConfigThumbnail:
	# Toggle for creating thumbnails in stages.
	# TODO: make this section optional entirely
	enable: bool

	# Size of the thumbnail canvas.
	canvas_width: int
	canvas_height: int

	# Position settings of the screenshot on the canvas. Screenshots are scaled to canvas resolution.
	screenshot_position: _ConfigThumbnailPosition
	# Position settings of the "cover art" on the canvas. Cover art is scaled to canvas resolution.
	cover_position: _ConfigThumbnailPosition
	# Path of the "cover art" image. This path is always relative to the thumbnail directory.
	cover_filepath: Path = field(metadata=_path_field_config)

	# Position settings of the text.
	text_position: _ConfigThumbnailPosition
	# The specific font to use when printing text on the thumbnail.
	# This can be a relative or absolute path. If the path is relative, then locations are checked in this order:
	# 1. Thumbnail directory, 2. System locations, 3. Path relative to execution (not recommended for use)
	text_font: str
	# The font pointsize to use when printing text on the thumbnail.
	text_size: int

	# A list of positions that heads will be placed at. Extra options such as offset and scale are
	# accounted for as well.
	head_positions: List[_ConfigThumbnailPosition]
	# A list of indices dictating what positions should be filled first, also dictating the order of
	# layering of heads. Example: a list of [0, 2, 1] will place heads at positions 0, 2, and 1 in
	# that order with heads placed first being underneath heads placed last.
	head_order: List[int]
	# A dictionary of heads. The keys of each entry will be used for prompting what heads are wanted
	# during the staging process.
	heads: Dict[str, _ConfigThumbnailIcon]
	
	# Position settings of the game icon on the canvas.
	game_position: _ConfigThumbnailPosition
	# A dictionary of games. The keys of each entry will be used for prompting what heads are wanted
	# during the staging process.
	games: Dict[str, _ConfigThumbnailIcon]

@dataclass_json
@dataclass
class _ConfigWebhookBase:
	# Individual toggle for the webhook.
	enable: bool = True
	# Message of the webhook, independent of any extra embeded data sent.
	message: str = ""
	# URL of an image to be set as the message's icon.
	avatar_url: str = ""
	# Name of the message sender of the webhook message.
	username: str = ""
	# URL to send the webhook payload to.
	url: str = ""

@dataclass_json
@dataclass
class _ConfigWebhooks:
	# Webhooks are JSON data configurations meant to be sent to Discord for monitoring VodBot.
	# All of the webhook base configurations.
	pull_vod: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	pull_clip: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	pull_error: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	pull_job_done: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	export_video: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	export_error: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	export_job_done: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	upload_video: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	upload_error: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	upload_job_done: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())
	vodbot_error: _ConfigWebhookBase = field(default_factory=lambda: _ConfigWebhookBase())

	# Main toggle for sending webhooks.
	enable: bool = False
	# The default settings for a webhook, each setting below is used if an individual configuration
	# does not set/contain the corresponding setting.
	message: str = ""
	avatar_url: str = "https://github.com/FriendTeamInc/VodBot/raw/main/assets/logo.png"
	username: str = "VodBot Webhook"
	url: str = ""

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
	thumbnail: Path = field(default=DEFAULT_CONFIG_DIRECTORY/"thumbnail", metadata=_path_field_config)

@dataclass_json
@dataclass
class Config:
	# The original copy of the config, the default.
	channels: List[_ConfigChannel] = field(default_factory=lambda: {})
	pull: _ConfigPull = field(default_factory=lambda: _ConfigPull())
	chat: _ConfigChat = field(default_factory=lambda: _ConfigChat())
	stage: _ConfigStage = field(default_factory=lambda: _ConfigStage())
	export: _ConfigExport = field(default_factory=lambda: _ConfigExport())
	upload: _ConfigUpload = field(default_factory=lambda: _ConfigUpload())
	thumbnail: _ConfigThumbnail = field(default_factory=lambda: _ConfigThumbnail())
	webhooks: _ConfigWebhooks = field(default_factory=lambda: _ConfigWebhooks())
	directories: _ConfigDirectories = field(default_factory=lambda: _ConfigDirectories())


DEFAULT_CONFIG_SCHEMA = Config.schema()
