# Initialization of VodBot, setting up configs, etc.

import vodbot.util as util
import vodbot.printer as cp

def run(args):
	pass
	# TODO: should run a bunch of input() prompts asking for info to set up VodBot

	# Ask for channels
	cp.cprint("Enter the login names of the Twitch channels you'd like to have archived.")
	cp.cprint("Example: the url is `https://twitch.tv/notquiteapex`, enter `notquiteapex`")
	while True:
		break

	# Ask for timezone (list out some common ones from pytz)
	cp.cprint("Enter the timezone for timedate referencing.")

	# ask for directories (have defaults ready)
	cp.cprint("Enter where VODs should be stored. Default (``)")
	cp.cprint("Enter where Clips should be stored. Default (``)")
	cp.cprint("Enter where temporary data should be stored. Default (``)")
	cp.cprint("Enter where staged data should be stored. Default (``)")

	# ready to write it all, go!
	cp.cprint("Writing config...")

	# list the location of the config and say what can be edited outside this command
	cp.cprint("Finished, the config can be edited at ``.")
