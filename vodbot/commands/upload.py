# Upload, command to upload staged videos to YouTube
# References:
# https://developers.google.com/youtube/v3/guides/uploading_a_video
# https://learndataanalysis.org/how-to-upload-a-video-to-youtube-using-youtube-data-api-in-python/

from .stage import StageData

import vodbot.util as util
import vodbot.video as vbvid
from vodbot.printer import cprint

import json
import pickle
import subprocess
from datetime import datetime
from pathlib import Path
from os import remove as os_remove
from os.path import exists as os_exists, isfile as os_isfile
from time import sleep

from httplib2.error import HttpLib2Error, HttpLib2ErrorWithResponse

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError, ResumableUploadError
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


# Default path
vodbotdir = util.vodbotdir
stagedir = None
tempdir = None

RETRIABLE_EXCEPTS = (HttpLib2Error, HttpLib2ErrorWithResponse, IOError)


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def upload_video(conf, service, stagedata):
	tmpfile = None
	try:
		tmpfile = vbvid.process_stage(conf, stagedata)
	except vbvid.FailedToSlice as e:
		cprint(f"#r#fRSkipping stage `{stagedata.id}`, failed to slice video with ID of `{e.vid}`.#r\n")
	except vbvid.FailedToConcat:
		cprint(f"#r#fRSkipping stage `{stagedata.id}`, failed to concatenate videos.#r\n")
	except vbvid.FailedToCleanUp as e:
		cprint(f"#r#fRSkipping stage `{stagedata.id}`, failed to clean up temp files.#r\n\n{e.vid}")

	# send request to youtube to upload
	request_body = {
		"snippet": {
			"categoryId": 20,
			"title": stagedata.title,
			"description": stagedata.desc
		},
		"status": {
			"privacyStatus": "private",
			"selfDeclaredMadeForKids": False
		}
	}

	# create media file, 100 MiB chunks
	media_file = MediaFileUpload(str(tmpfile), chunksize=1024*1024*100, resumable=True)

	# create upload request and execute
	response_upload = service.videos().insert(
		part="snippet,status",
		body=request_body,
		media_body=media_file
	)

	resp = None
	errn = 0
	cprint(f"#fCUploading stage #r`#fM{stagedata.id}#r`, progress: #fC0#fY%#r #d...#r", end="\r")
	while resp is None:
		try:
			status, resp = response_upload.next_chunk()
			if status:
				cprint(f"#fCUploading stage #r`#fM{stagedata.id}#r`, progress: #fC{int(status.progress()*100)}#fY%#r #d...#r", end="\r")
			if resp is not None:
				if "id" in resp:
					cprint(f"#fCUploading stage #r`#fM{stagedata.id}#r`, progress: #fC100#fY%#r!")
					cprint(f"#l#fGVideo was successfully uploaded!#r #dhttps://youtu.be/{resp['id']}#r")
				else:
					util.exit_prog(99, f"Unexpected upload failure occurred, \"{resp}\"")
		except ResumableUploadError as err:
			if err.resp.status in [400, 401, 402, 403]:
				try:
					jsondata = json.loads(err.content)['error']['errors'][0]
					util.exit_prog(40, f"API Error: `{jsondata['reason']}`. Message: `{jsondata['message']}`")
				except (json.JSONDecodeError, KeyError):
					util.exit_prog(40, f"Unknown API Error has occured, ({err.resp.status}, {err.content})")
			print(f"A Resumeable error has occured, retrying in 5 sec... ({err.resp.status}, {err.content})")
			errn += 1
			sleep(5)
		except HttpError as err:
			if err.resp.status in [500, 502, 503, 504]:
				print(f"An HTTP error has occured, retrying in 5 sec... ({err.resp.status}, {err.content})")
				errn += 1
				sleep(5)
			else:
				raise
		except RETRIABLE_EXCEPTS as err:
			print(f"An HTTP error has occured, retrying in 5 sec... ({err})")
			errn += 1
			sleep(5)
		
		if errn >= 10:
			print("Skipping, errored too many times.")
			break
	else:
		if conf["stage_upload_delete"]:
			try:
				os_remove(str(stagedir / f"{stagedata.id}.stage"))
			except:
				util.exit_prog(90, f"Failed to remove stage `{stagedata.id}` after upload.")

		try:
			os_remove(str(tmpfile))
		except:
			util.exit_prog(90, f"Failed to remove temp slice file of stage `{stagedata.id}` after upload.")


def run(args):
	# load config
	conf = util.load_conf(args.config)

	# configure variables
	global stagedir, tempdir
	tempdir = Path(conf["temp_dir"])
	stagedir = Path(conf["stage_dir"])
	PICKLE_FILE = conf["youtube_pickle_path"]
	CLIENT_SECRET_FILE = conf["youtube_client_path"]
	API_NAME = 'youtube'
	API_VERSION = 'v3'
	SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

	# handle logout
	if args.id == "logout":
		try:
			os_remove(PICKLE_FILE)
			cprint("#dLogged out of Google API session#r")
		except:
			util.exit_prog(11, "Failed to remove credentials for YouTube account.")
		
		return
	
	# load stages, but dont upload
	# Handle id/all
	stagedata = None
	stagedatas = None
	if args.id == "all":
		cprint("#dLoading stages...", end=" ")
		# create a list of all the hashes and sort by date streamed, upload chronologically
		stagedatas = StageData.load_all_stages(stagedir)
		stagedatas.sort(key=sort_stagedata)
	else:
		cprint("#dLoading stage...", end=" ")
		# check if stage exists, and prep it for upload
		stagedata = StageData.load_from_id(stagedir, args.id)
		cprint(f"About to upload stage {stagedata.id}.#r")

	# authenticate youtube service
	if not os_exists(CLIENT_SECRET_FILE):
		util.exit_prog(19, "Missing YouTube Client ID/Secret file.")

	cprint("Authenticating with Google...", end=" ")

	service = None
	credentials = None

	if os_exists(PICKLE_FILE):
		with open(PICKLE_FILE, "rb") as f:
			credentials = pickle.load(f)
	
	if not credentials or credentials.expired:
		try:
			if credentials and credentials.expired and credentials.refresh_token:
				credentials.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
				credentials = flow.run_console()
		except RefreshError:
			flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
			credentials = flow.run_console()
		
		with open(PICKLE_FILE, "wb") as f:
			pickle.dump(credentials, f)
	
	try:
		service = build(API_NAME, API_VERSION, credentials=credentials)
	except Exception as err:
		util.exit_prog(50, f"Failed to connect to YouTube API, \"{err}\"")
	
	cprint("Authenticated.", end=" ")
	
	# Handle id/all
	if args.id == "all":
		# begin to upload
		cprint(f"About to upload {len(stagedatas)} stages.#r")
		for stage in stagedatas:
			upload_video(conf, service, stage)
	else:
		# upload stage
		cprint(f"About to upload stage {stagedata.id}.#r")
		upload_video(conf, service, stagedata)
	
