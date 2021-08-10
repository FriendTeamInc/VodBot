# Initialization of VodBot, setting up config, etc.

import json
from os.path import isabs

import vodbot.util as util
import vodbot.printer as cp

vodbotdir = util.vodbotdir
DEFAULT_CONF = util.DEFAULT_CONF

def run(args):
	pass
	# TODO: should run a bunch of input() prompts asking for info to set up VodBot
	# TODO: allow passing of arguments to not require input

	channels = []
	timezone = "" # switch to UTC only
	voddir = ""
	clipdir = ""
	tempdir = ""
	stagedir = ""

	# Ask for channels
	if not args.channels:
		cp.cprint("Enter the login names of the Twitch channels you'd like to have archived.")
		cp.cprint("When you're done, just leave the input empty and press enter.")
		cp.cprint("Example: the url is `https://twitch.tv/notquiteapex`, enter `notquiteapex`")
		while True:
			channel = input("> ")
			if channel == "":
				break
			elif channel.isalnum():
				cp.cprint("Error, channel names must be alphanumeric.")
			else:
				channels += [channel]
	else:
		channels = args.channels

	# Ask for timezone (list out some common ones from pytz)
	
	if not args.timezone:
		cp.cprint("Enter the timezone for timedate referencing.")
	else:
		timezone = args.timezone
		# check that entered timezone is valid

	# ask for directories (have defaults ready)
	cp.cprint("Now let's get some directories to store data. The entered paths must be absolute, not relative.")
	cp.cprint("If you'd like to use the default location listed, just leave the input blank and press enter.")

	if not args.voddir:
		while True:
			cp.cprint(f"Enter where VODs should be stored.\nDefault: `{DEFAULT_CONF['vod_dir']}`")
			voddir = input("> ")
			if voddir == "":
				voddir = DEFAULT_CONF['vod_dir']
				break
			elif not isabs(voddir):
				cp.cprint(f"Error, path `{voddir}` is not an absolute path.")
			else:
				break
	else:
		voddir = args.voddir

	if not args.clipdir:
		cp.cprint(f"Enter where Clips should be stored. Default: `{DEFAULT_CONF['clip_dir']}`")
		clipdir = input("> ")
	else:
		clipdir = args.clipdir

	if not args.tempdir:
		cp.cprint("Enter where temporary data should be stored. Default (``)")
		tempdir = input("> ")
	else:
		tempdir = args.tempdir

	if not args.stagedir:
		cp.cprint("Enter where staged data should be stored. Default (``)")
		stagedir = input("> ")
	else:
		stagedir = args.stagedir


	# ready to write it all, go!
	cp.cprint("Writing config...")
	# Edit default config variable and write that to file.
	DEFAULT_CONF['twitch_channels'] = channels
	DEFAULT_CONF['stage_timezone'] = timezone
	DEFAULT_CONF['vod_dir'] = voddir
	DEFAULT_CONF['clip_dir'] = clipdir
	DEFAULT_CONF['temp_dir'] = tempdir
	DEFAULT_CONF['stage_dir'] = stagedir

	# list the location of the config and say what can be edited outside this command
	cp.cprint("Finished, the config can be edited at ``.")
