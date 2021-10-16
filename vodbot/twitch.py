# Module to make API calls to Twitch.tv

from .itd import gql

import json


# for escaping strings, taken from json.py
ENCODE_DICT = {
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

DECODE_DICT = dict((v,k) for k,v in ENCODE_DICT.items())

CHAT_STATE = [
	"PUBLISHED",
	"UNPUBLISHED",
	"PENDING_REVIEW",
	"PENDING_REVIEW_SPAM",
	"DELETED"
]

class Vod:
	def __init__(self, json):
		self.id = json["id"]
		self.user_id = json["creator"]["id"]
		self.user_login = json["creator"]["login"]
		self.user_name = json["creator"]["displayName"]

		if json["game"]:
			self.game_id = json["game"]["id"]
			self.game_name = json["game"]["name"]
		else:
			self.game_id = ""
			self.game_name = ""

		self.title = json["title"]
		self.created_at = json["publishedAt"]
		self.length = json["lengthSeconds"]
		
		self.url = f"twitch.tv/videos/{self.id}"
	
	def __repr__(self):
		return f"VOD({self.id}, {self.created_at}, {self.user_name}, {self.created_at}, {self.duration})"
	
	def write_meta(self, filename):
		jsondict = {
			"id": self.id,
			"user_id": self.user_id,
			"user_login": self.user_login,
			"user_name": self.user_name,
			"game_id": self.game_id,
			"game_name": self.game_name,
			"title": self.title,
			"created_at": self.created_at,
			"length": self.length
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)


class Clip:
	def __init__(self, json):
		self.id = json["id"]
		self.slug = json["slug"]
		self.user_id = json["broadcaster"]["id"]
		self.user_login = json["broadcaster"]["login"]
		self.user_name = json["broadcaster"]["displayName"]

		if not json["curator"]:
			self.clipper_id = self.user_id
			self.clipper_login = self.user_login
			self.clipper_name = self.user_name
		else:
			self.clipper_id = json["curator"]["id"]
			self.clipper_login = json["curator"]["login"]
			self.clipper_name = json["curator"]["displayName"]

		if json["game"]:
			self.game_id = json["game"]["id"]
			self.game_name = json["game"]["name"]
		else:
			self.game_id = ""
			self.game_name = ""

		self.title = json["title"]
		self.created_at = json["createdAt"]
		self.view_count = json["viewCount"]
		self.length = json["durationSeconds"]
		
		self.url = f"twitch.tv/{self.user_name}/clip/{self.id}"
	
	def __repr__(self):
		return f"Clip({self.title}, {self.created_at}, {self.user_name}, {self.clipper_name})"
	
	def write_meta(self, filename):
		jsondict = {
			"id": self.id,
			"slug": self.slug,
			"user_id": self.user_id,
			"user_login": self.user_login,
			"user_name": self.user_name,
			"clipper_id": self.clipper_id,
			"clipper_login": self.clipper_login,
			"clipper_name": self.clipper_name,
			"game_id": self.game_id,
			"game_name": self.game_name,
			"title": self.title,
			"created_at": self.created_at,
			"view_count": self.view_count,
			"length": self.length
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)


class Channel:
	def __init__(self, json):
		self.id = json["id"]
		self.login = json["login"]
		self.display_name = json["displayName"]
		self.created_at = json["createdAt"]
	
	def __repr__(self):
		return f"Channel({self.id}, {self.display_name})"


class ChatMessage:
	def __init__(self, json) -> None:
		self.user = json["commenter"]["displayName"]
		self.user_color = json["message"]["userColor"] or "FFFFFF"
		self.user_color = self.user_color.strip("#")

		self.message = ""
		for frag in json["message"]["fragments"]:
			if frag["mention"] is not None:
				self.message += "@" + frag["mention"]["displayName"]
			self.message += frag["text"]
			self.message += " "
		self.message = self.message.strip()


		self.offset_secs = json["contentOffsetSeconds"]
		self.state = json["state"]

		self.encoded_message = self.encode_message(self.message)
		self.encoded_state = self.encode_state(self.state)
		
	def __repr__(self):
		return f"ChatMessage(ofst={self.offset_secs};user={self.user};msg=\"{self.message}\")"
		
	def write_dict(self):
		return {
			"ofst":self.offset_secs,
			"state":self.state,
			"clr":self.user_color,
			"user":self.user,
			"msg":self.message
		}
	
	@staticmethod
	def encode_message(msg):
		for k,v in ENCODE_DICT.items():
			msg = msg.replace(k, v)
		
		return msg
	
	@staticmethod
	def decode_message(msg):
		for k,v in DECODE_DICT.items():
			msg = msg.replace(k, v)
		
		return msg
	
	@staticmethod
	def encode_state(state):
		return CHAT_STATE.index(state)
	
	@staticmethod
	def decode_state(state):
		return CHAT_STATE[state]



def get_channels(channel_ids: list):
	"""
	Uses a (blocking) HTTP request to retrieve channel information from Twitch's API.

	:param channel_ids: A list of channel login name strings.
	:returns: A list of Channel objects.
	"""

	# Make channel objects and store them in a list
	channels = []
	for channel_id in channel_ids:
		query = gql.GET_CHANNEL_QUERY.format(channel_id=channel_id)
		resp = gql.gql_query(query=query).json()
		if resp["data"]["user"] == None:
			raise Exception(f"Channel `{channel_id}` does not exist!")
		channels.append(Channel(resp["data"]["user"]))
	
	return channels


def get_channel_vods(channel: Channel):
	"""
	Uses a (blocking) HTTP request to retrieve VOD info for a specific channel.

	:param channel: A Channel object.
	:returns: A list of VOD objects.
	"""

	vods = []
	pagination = ""
	while True:
		query = gql.GET_CHANNEL_VIDEOS_QUERY.format(
			channel_id=channel.login,
			after=pagination, first=100,
			type="ARCHIVE", sort="TIME"
		)
		resp = gql.gql_query(query=query).json()
		resp = resp ["data"]["user"]["videos"]

		if not resp or not resp["edges"]:
			break

		pagination = resp["edges"][-1]["cursor"]
		
		for vod in resp["edges"]:
			vods.append(Vod(vod["node"]))

		if pagination == "" or pagination == None:
			break

	return vods


def get_channel_clips(channel):
	"""
	Uses a (blocking) HTTP request to retrieve Clip info for a specific channel.

	:param channel: A Channel object.
	:returns: A list of Clip objects.
	"""

	clips = []
	pagination = ""
	while True:
		query = gql.GET_CHANNEL_CLIPS_QUERY.format(
			channel_id=channel.login,
			after=pagination, first=100
		)
		resp = gql.gql_query(query=query).json()
		resp = resp["data"]["user"]["clips"]

		if not resp or not resp["edges"]:
			break

		pagination = resp["edges"][-1]["cursor"]
		
		for clip in resp["edges"]:
			clips.append(Clip(clip["node"]))

		if pagination == "" or pagination == None:
			break

	return clips


def get_video_comments(video_id):
	"""
	Uses a (blocking) HTTP request to retrieve chat logs for a specific video.

	:param video_id: A video ID string.
	:returns: A list of ChatMessage objects.
	"""

	messages = []
	pagination = ""
	while True:
		query = gql.GET_VIDEO_COMMENTS_QUERY.format(
			video_id=video_id, first=100, after=pagination
		)
		resp = gql.gql_query(query=query).json()
		resp = resp["data"]["video"]["comments"]

		if not resp or not resp["edges"]:
			break

		pagination = resp["edges"][-1]["cursor"]
		for comment in resp["edges"]:
			messages.append(ChatMessage(comment["node"]))
		
		if pagination == "" or pagination == None:
			break
	
	return messages
