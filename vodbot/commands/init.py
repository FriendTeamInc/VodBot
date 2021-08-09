# Initialization of VodBot, setting up config, etc.

import json

import vodbot.util as util
import vodbot.printer as cp

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
		cp.cprint("Example: the url is `https://twitch.tv/notquiteapex`, enter `notquiteapex`")
		while True:
			channel = input("> ")
			# TODO: check that channel is only alphanumeric (or whatever twitch's restrictions are)
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
	if not args.voddir:
		cp.cprint("Enter where VODs should be stored. Default (``)")
		voddir = input("> ")
	else:
		voddir = args.voddir

	if not args.clipdir:
		cp.cprint("Enter where Clips should be stored. Default (``)")
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
	conf = {
		
	}

	# list the location of the config and say what can be edited outside this command
	cp.cprint("Finished, the config can be edited at ``.")
