# Module to make API calls to Twitch.tv

from . import TWITCH_CLIENT_ID
from .itd import gql

import requests
import json

class Vod:
	def __init__(self, json):
		self.id = json["id"] # url: twitch.tv/videos/{id}
		self.user_id = json["user_id"]
		self.user_name = json["user_name"]
		self.title = json["title"]
		self.created_at = json["created_at"]
		self.duration = json["duration"]
		
		self.url = f"twitch.tv/videos/{self.id}"
	
	def __repr__(self):
		return f"VOD({self.id}, {self.created_at}, {self.user_name}, {self.created_at}, {self.duration})"
	
	def write_meta(self, filename):
		jsondict = {
			"id": self.id,
			"user_id": self.user_id,
			"user_name": self.user_name,
			"title": self.title,
			"created_at": self.created_at,
			"duration": self.duration
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)


class Clip:
	def __init__(self, json):
		self.id = json["id"] # url: twitch.tv/videos/{id}
		self.user_id = json["broadcaster_id"]
		self.user_name = json["broadcaster_name"]
		self.clipper_id = json["creator_id"]
		self.clipper_name = json["creator_name"]
		self.title = json["title"]
		self.created_at = json["created_at"]
		self.view_count = json["view_count"]
		
		self.url = f"twitch.tv/{self.user_name}/clip/{self.id}"
	
	def __repr__(self):
		return f"Clip({self.title}, {self.created_at}, {self.user_name}, {self.clipper_name})"
	
	def write_meta(self, filename):
		jsondict = {
			"id": self.id,
			"user_id": self.user_id,
			"user_name": self.user_name,
			"clipper_id": self.clipper_id,
			"clipper_name": self.clipper_name,
			"title": self.title,
			"created_at": self.created_at,
			"view_count": self.view_count
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)


class Channel:
	def __init__(self, json):
		self.id = json["id"]
		self.login = json["login"]
		self.display_name = json["display_name"]
		self.created_at = json["created_at"]
	
	def __repr__(self):
		return f"Channel({self.id}, {self.display_name})"


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
			channel_id=channel.id,
			after=pagination, first=100,
			type="ARCHIVE", sort="TIME"
		)
		resp = gql.gql_query(query=query).json()
		resp = resp ["data"]["user"]["videos"]

		if not resp["edges"]:
			break

		pagination = resp["edges"][-1]["cursor"]
		
		for vod in resp["data"]["edges"]:
			vods.append(Vod(vod))

		if pagination == "":
			break;

	return vods


def get_channel_clips(channel):
	"""
	Uses a (blocking) HTTP request to retrieve Clip info for a specific channel.

	:param channel: A Channel object.
	:returns: A list of Clip objects.
	"""

	vods = []
	pagination = ""
	while True:
		query = gql.GET_CHANNEL_CLIPS_QUERY.format(
			channel_id=channel.id,
			after=pagination, first=100,
			period="ALL_TIME"
		)
		resp = gql.gql_query(query=query).json()
		resp = resp ["data"]["user"]["videos"]

		if not resp["edges"]:
			break

		pagination = resp["edges"][-1]["cursor"]
		
		for vod in resp["data"]["edges"]:
			vods.append(Clip(vod))

		if pagination == "":
			break;

	return vods
