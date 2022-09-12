# Upload, command to upload staged videos to YouTube
# References:
# https://developers.google.com/docs/api/quickstart/python
# https://developers.google.com/youtube/v3/guides/uploading_a_video
# https://learndataanalysis.org/how-to-upload-a-video-to-youtube-using-youtube-data-api-in-python/

from ..cache import load_cache, save_cache
from .stage import StageData

import vodbot.util as util
import vodbot.video as vbvid
import vodbot.chatlog as vbchat
from vodbot.printer import cprint
from vodbot.config import Config

import json
from datetime import datetime
from pathlib import Path
from os import remove as os_remove
from os.path import exists as os_exists
from time import sleep

from httplib2.error import HttpLib2Error, HttpLib2ErrorWithResponse

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError, ResumableUploadError
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials


RETRIABLE_EXCEPTS = (HttpLib2Error, HttpLib2ErrorWithResponse, IOError)


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def _upload_artifact(media_file, upload_string, response_upload, tmpfile, stagedata, getting_video=False):
	video_id = "" # youtube video id
	resp = None
	errn = 0

	while resp is None:
		try:
			status, resp = response_upload.next_chunk()
			if status:
				cprint(f"#fCUploading {upload_string}, progress: #fC{int(status.progress()*100)}#fY%#r #d...#r", end="\r")
			if resp is not None:
				cprint(f"#fCUploading {upload_string}, progress: #fC100#fY%#r!")
				if getting_video:
					cprint(f"#l#fGVideo was successfully uploaded!#r #dhttps://youtu.be/{resp['id']}#r")
					video_id = resp["id"]
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
			if getting_video:
				print("Skipping video upload, errored too many times.")
				return ""
			else:
				print("Skipping chatlog upload, errored too many times.")
				return False
	
	if getting_video:
		return video_id
	else:
		return True


def upload_video(conf: Config, service, stagedata: StageData) -> str:
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
		notifySubscribers=False,
		media_body=media_file
	)

	cprint(f"#fCUploading stage #r`#fM{stagedata.id}#r`, progress: #fC0#fY%#r #d...#r", end="\r")
	uploaded = _upload_artifact(media_file, f"stage #r`#fM{stagedata.id}#r`", response_upload, str(tmpfile), stagedata, getting_video=True)

	try:
		# delete vars to release the files
		del media_file
		del response_upload
		sleep(1)
		os_remove(str(tmpfile))
	except Exception as e:
		util.exit_prog(90, f"Failed to remove temp slice file of stage `{stagedata.id}` after upload. {e}")
	
	return uploaded


def upload_captions(conf: Config, service, stagedata: StageData, vid_id: str) -> bool:
	tmpfile = vbchat.process_stage(conf, stagedata, "upload")

	if tmpfile == False:
		return True

	request_body = {
		"snippet": {
			"name": "Chat",
			"videoId": vid_id,
			"language": "en"
		}
	}

	media_file = MediaFileUpload(str(tmpfile), chunksize=1024*1024*100, resumable=True)

	response_upload = service.captions().insert(
		part="snippet",
		body=request_body,
		sync=False,
		media_body=media_file
	)

	cprint(f"#fCUploading stage chatlog #r`#fM{stagedata.id}#r`, progress: #fC0#fY%#r #d...#r", end="\r")
	uploaded = _upload_artifact(media_file, f"stage chatlog #r`#fM{stagedata.id}#r`", response_upload, str(tmpfile), stagedata, getting_video=False)
	
	try:
		# delete vars to release the files
		del media_file
		del response_upload
		sleep(1)
		os_remove(str(tmpfile))
	except Exception as e:
		util.exit_prog(90, f"Failed to remove temp slice file of stage `{stagedata.id}` after upload. {e}")

	return uploaded


def run(args):
	# load config
	conf = util.load_conf(args.config)
	cache = load_cache(conf, args.cache_toggle)

	# configure variables
	STAGE_DIR = conf.directories.stage
	SESSION_FILE = conf.upload.session_path
	CLIENT_FILE = conf.upload.client_path

	API_NAME = 'youtube'
	API_VERSION = 'v3'
	SCOPES = [ # Only force-ssl is required, but both makes it explicit.
		"https://www.googleapis.com/auth/youtube.upload",   # Videos.insert
		"https://www.googleapis.com/auth/youtube.force-ssl" # Captions.insert
	]

	# handle logout
	if args.id == "logout":
		try:
			os_remove(SESSION_FILE)
			cprint("#dLogged out of Google API session#r")
		except:
			util.exit_prog(11, "Failed to remove credentials for YouTube account.")
		
		return
	
	# load stages, but dont upload
	# Handle id/all
	stagedatas = None
	if args.id == "all":
		cprint("#dLoading stages...", end=" ")
		# create a list of all the hashes and sort by date streamed, upload chronologically
		stagedatas = StageData.load_all_stages(STAGE_DIR)
		stagedatas.sort(key=sort_stagedata)
	else:
		cprint("#dLoading stage...", end=" ")
		# check if stage exists, and prep it for upload
		stagedatas = [StageData.load_from_id(STAGE_DIR, args.id)]

	# authenticate youtube service
	if not os_exists(CLIENT_FILE):
		util.exit_prog(19, "Missing YouTube Client ID/Secret file.")

	cprint("Authenticating with Google...", end=" ")

	service = None
	creds = None

	if os_exists(SESSION_FILE):
		creds = Credentials.from_authorized_user_file(SESSION_FILE, SCOPES)
	
	if not creds or not creds.valid:
		try:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
				creds = flow.run_console()
		except RefreshError:
			flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
			creds = flow.run_console()
		
		with open(SESSION_FILE, "w") as f:
			f.write(creds.to_json())
	
	try:
		service = build(API_NAME, API_VERSION, credentials=creds)
	except Exception as err:
		util.exit_prog(50, f"Failed to connect to YouTube API, \"{err}\".")
	
	cprint("Authenticated.", end=" ")
	
	# begin to upload
	cprint(f"About to upload {len(stagedatas)} stages.#r")
	for stage in stagedatas:
		video_id = upload_video(conf, service, stage)
		if video_id is not None:
			if conf.upload.chat_enable:
				upload_captions(conf, service, stage, video_id)
			
			if conf.stage.delete_on_upload:
				try:
					os_remove(STAGE_DIR / f"{stage.id}.stage")
					cache.stages.remove(stage.id)
					save_cache(conf, cache)
				except:
					util.exit_prog(90, f"Failed to remove stage `{stage.id}` after upload.")
		print()
