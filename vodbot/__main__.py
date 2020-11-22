from .util import exit_prog

import os
from pathlib import Path

def main():
	vodbotdir = str(Path.home() / ".vodbot")

	if not os.path.exists(vodbotdir):
		if not os.path.isdir(vodbotdir):
			exit_prog(54, f"Non-directory object \"{vodbotdir}\" must be removed before proceeding!")
		
		os.mkdir(vodbotdir)

		basetoml = {
			"twitch": {
				"client-id":"PUT TWITCH CLIENT-ID HERE",
				"watch-channels":["notquiteapex","juicibox","batkigu"]
			}
		}

	# GET https://api.twitch.tv/helix/users: get User-IDs with this, using the watch channels list
	# GET https://api.twitch.tv/helix/videos: get videos using the IDs

	try:
		pass
	except FileNotFoundError:
		pass
	print("Hello, World!")


if __name__ == "__main__":
	main()
