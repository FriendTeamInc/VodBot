# Module to make API calls to Twitch.tv

from typing import List
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

# TODO: change to enum?
CHAT_STATE = [
	"PUBLISHED", "UNPUBLISHED",
	"PENDING_REVIEW", "PENDING_REVIEW_SPAM",
	"DELETED"
]

class VodChapter:
	def __init__(self,
		position:int, duration:int, type:str, description:str
	):
		self.position = position
		self.duration = duration
		self.type = type
		self.description = description

	def __repr__(self):
		return f"VodChapter({self.position}, {self.duration}, {self.created_at}, {self.description})"

	def to_dict(self):
		return {"pos":self.position, "dur":self.duration, "type":self.type, "desc":self.description}

class Vod:
	def __init__(self,
		id:str, user_id:str, user_login:str, user_name:str, title:str,
		created_at:str, length:int, chapters:List[VodChapter],
		game_id:str="", game_name:str="",
		has_chat:bool = False
	):
		self.id = id
		self.user_id = user_id
		self.user_login = user_login
		self.user_name = user_name

		self.game_id = game_id
		self.game_name = game_name

		self.chapters = chapters

		self.title = title
		self.created_at = created_at
		self.length = length
		
		self.url = f"twitch.tv/videos/{self.id}"

		self.has_chat = has_chat
	
	def __repr__(self):
		return f"Vod({self.id}, {self.created_at}, {self.user_name}, {self.duration})"
	
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
			"length": self.length,
			"has_chat": self.has_chat,
			"chapters": [x.to_dict() for x in self.chapters]
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)


class Clip:
	def __init__(self, id:str, slug:str, title:str, created_at:str, 
		user_id:str, user_login:str, user_name:str,
		clipper_id:str, clipper_login:str, clipper_name:str,
		game_id:str, game_name:str, view_count:int, length:int,
		offset:int, video_id:str
	):
		self.id = id # id of the clip itself
		self.slug = slug # the url ending to identify the clip
		self.user_id = user_id # user streaming
		self.user_login = user_login
		self.user_name = user_name

		self.clipper_id = clipper_id # user who clipped stream
		self.clipper_login = clipper_login
		self.clipper_name = clipper_name

		self.game_id = game_id # the "game" being played
		self.game_name = game_name

		self.title = title # clip metadata
		self.created_at = created_at
		self.view_count = view_count
		self.length = length

		self.offset = offset # offset from the start of the stream the clip was made
		self.video_id = video_id # id of the video stream the clip was made of
		
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
			"length": self.length,
			"offset": self.offset,
			"video_id": self.video_id
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)


class Channel:
	def __init__(self, id:str, login:str, display_name:str, created_at:str):
		self.id = id
		self.login = login
		self.display_name = display_name
		self.created_at = created_at
	
	def __repr__(self):
		return f"Channel({self.id}, {self.display_name})"


class ChatMessage:
	def __init__(self,
		user:str, color:str, offset:int, msg:str=None, state:str=None,
		enc_msg:str=None, enc_state:str=None
	):
		self.user = user
		self.color = color
		self.offset = offset

		if msg is not None:
			self.msg = msg
			self.enc_msg = self.encode_message(self.msg)
		elif enc_msg is not None:
			self.enc_msg = enc_msg
			self.msg = self.decode_message(self.enc_msg)
		else:
			raise Exception(f"Could not determine message from constructor for ChatMessage. (\"{msg}\") (\"{enc_msg}\")")

		if state is not None:
			self.state = state
			self.enc_state = self.encode_state(self.state)
		elif enc_state is not None:
			self.enc_state = enc_state
			self.state = self.decode_state(self.enc_state)
		else:
			raise Exception(f"Could not determine state from constructor for ChatMessage. (\"{state}\") (\"{enc_state}\")")
		
	def __repr__(self):
		return f"ChatMessage(ofst={self.offset};{self.user}: {self.msg})"
		
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


def get_channels(channel_ids: List[str]) -> List[Channel]:
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
		c = resp["data"]["user"]

		if c == None:
			raise Exception(f"Channel `{channel_id}` does not exist!")
		
		channels.append(
			Channel(
				id=c["id"], login=c["login"],
				display_name=c["displayName"], created_at=c["createdAt"]
			)
		)
	
	return channels


def get_channel_vods(channel: Channel) -> List[Vod]:
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
			v = vod["node"]
			c = v["creator"]
			g = v["game"]

			game_id = ""
			game_name = ""
			if g:
				game_id = g["id"]
				game_name = g["name"]
			
			
			# Get stream chapter info now
			chapters = []
			chapter_page = ""
			while True:
				query = gql.GET_VIDEO_CHAPTERS.format(
					id=v["id"], after=chapter_page
				)
				resp = gql.gql_query(query=query).json()
				resp = resp["data"]["video"]["moments"]
				
				if not resp or not resp["edges"]:
					break
				chapter_page = resp["edges"][-1]["cursor"]

				for chap in resp["edges"]:
					n = chap["node"]
					chapters.append(
						VodChapter(
							type=n["type"], description=n["description"],
							position=int(n["positionMilliseconds"]/1000),
							duration=int(n["durationMilliseconds"]/1000)
						)
					)
				
				if chapter_page == "" or chapter_page == None:
					break

			vods.append(
				Vod(
					id=v["id"], length=v["lengthSeconds"], title=v["title"],
					user_id=c["id"], user_login=c["login"], user_name=c["displayName"], 
					game_id=game_id, game_name=game_name, created_at=v["publishedAt"],
					chapters=chapters
				)
			)

		if pagination == "" or pagination == None:
			break


	return vods


def get_channel_clips(channel: Channel) -> List[Clip]:
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
			c = clip["node"]
			b = c["broadcaster"]
			w = c["curator"]
			g = c["game"]
			v = c["video"]
			v_id = "unknown"
			if v is not None:
				v_id = v["id"]

			w_id = b["id"]
			w_login = b["login"]
			w_name = b["displayName"]
			if w is not None:
				w_id = w["id"]
				w_login = w["login"]
				w_name = w["displayName"]
			
			g_id = ""
			g_name = ""
			if g is not None:
				g_id = g["id"]
				g_name = g["name"]

			clips.append(
				Clip(
					id=c["id"], slug=c["slug"], created_at=c["createdAt"],
					user_id=b["id"], user_login=b["login"], user_name=b["displayName"],
					clipper_id=w_id, clipper_login=w_login, clipper_name=w_name,
					game_id=g_id, game_name=g_name, title=c["title"],
					view_count=c["viewCount"], length=c["durationSeconds"],
					offset=c["videoOffsetSeconds"] or 0, video_id=v_id
				)
			)

		if pagination == "" or pagination == None:
			break

	return clips


def get_video_comments(video_id: str) -> List[ChatMessage]:
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
			c = comment["node"]

			usr = c["commenter"]["displayName"]
			clr = c["message"]["userColor"] or "FFFFFF"
			clr = clr.strip("#")

			msg = ""
			for frag in c["message"]["fragments"]:
				if frag["mention"] is not None:
					msg += "@" + frag["mention"]["displayName"]
				msg += frag["text"]
				msg += " "
			msg = msg.strip()

			ofst = c["contentOffsetSeconds"]
			state = c["state"]

			messages.append(
				ChatMessage(
					user=usr, color=clr, msg=msg, offset=ofst, state=state
				)
			)
		
		if pagination == "" or pagination == None:
			break
	
	return messages
