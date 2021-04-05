# Upload, command to upload staged videos to YouTube
# References:
# https://developers.google.com/youtube/v3/guides/uploading_a_video
# https://learndataanalysis.org/how-to-upload-a-video-to-youtube-using-youtube-data-api-in-python/

import vodbot.util as util
import pickle
from datetime import datetime
from os.path import exists as os_exists
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request


# Default path
vodbotdir = util.vodbotdir

CLIENT_SECRET_FILE = vodbotdir / 'youtube-conf.json'
API_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload_video(service, stage_id):
	# load stage from file, grab necessary info to put in the request body

	# send request to youtube to upload
	request_body = {
		"snippet": {
			"categoryId": 20
		}
	}

	# create media file
	media_file = MediaFileUpload()

	# create upload request and execute
	response_upload = service.videos().insert(
		part="snippet,status",
		body=request_body,
		media_body=media_file
	).execute()


def run(args):
	# authenticate youtube service
	service = None
	credentials = None
	pickle_filename = f"tkn_{API_NAME}_{API_VERSION}.pkl"

	if os_exists(str(vodbotdir / pickle_filename)):
		with open(str(vodbotdir / pickle_filename), "rb") as f:
			credentials = pickle.load(f)
	
	if not cred or not cred.valid:
		if cred and cred.expired and cred.refresh_token:
			cred.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
			cred = flow.run_local_server()
		
		with open(str(vodbotdir / pickle_filename), "wb") as f:
			pickle.dump(credentials, f)
	
	try:
		service = build(API_NAME, API_VERSION)
	except google.auth.exceptions.MutualTLSChannelError as err:
		util.exit_prog(50, f"Failed to connect to YouTube API, \"{err}\"")
	
	# Handle id/all
	if args.id == "all":
		# create a list of all the hashes and sort by date streamed, upload chronologically
		pass
	else:
		# check if stage exists, and prep it for upload
		if os_exists(str(vodbotdir / "stage" / (args.id+".stage"))):
			pass
		else:
			util.exit_prog(51, f"Could not find stage {args.id}")
