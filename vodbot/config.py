# Dedicated module for the config class and associated classes
# having a dedicated type makes accessing specific members easier and dictated

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
		self.api_use_alt = False
		self.api_client = ""
		self.api_secret = ""

class _ConfigStage():
	def __init__(self) -> None:
		pass

class _ConfigExport():
	def __init__(self) -> None:
		pass

class _ConfigUpload():
	def __init__(self) -> None:
		pass

class _ConfigThumbnail():
	
	def __init__(self) -> None:
		pass

class _ConfigWebhooks():
	def __init__(self) -> None:
		pass

class _ConfigDirectories():
	def __init__(self,
		vod:str, clip:str,
		temp:str, stage:str,
		thumbnail:str
	) -> None:
		self.vod = Path(vod)
		self.clip = Path(clip)
		self.temp = Path(temp)
		self.stage = Path(stage)
		self.thumbnail = Path(thumbnail)

class Config:
	def __init__(self) -> None:
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
