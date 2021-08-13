# Info, command to inspect a piece of media from Twitch

import re

PTR_VOD = [
	r"^(?P<id>\d+)?$",
	r"^(https?://)?(www\.)?twitch.tv/videos/(?P<id>\d+)(\?\.+)?$"
]
PTR_CLIP = [
	r"^(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)$",
	r"^(https?://)?(www\.)?twitch.tv/\w+/clip/(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)(\?\.+)?$",
	r"^(https?://)?clips\.twitch.tv/(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)(\?\.+)?$"
]
PTR_CHANNEL = [
	r"^[a-zA-Z0-9][\w]{0,24}$",
	r"^(https?://)?(www\.)?twitch\.tv/(?P<id>[a-zA-Z0-9][\w]{0,24})(\?.*)?$"
]

def run(args):
	# First determine what kind of data it is...
	# We should allow people to paste full links or just the ID too.
	cid = args.id

	# Channel
	# VOD
	# Clip

	# The call the appropriate info query for GQL

	# Read the data back and out to the terminal

	# Done!
	pass
