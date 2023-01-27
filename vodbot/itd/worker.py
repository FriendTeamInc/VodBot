from vodbot.config import Config
from vodbot.printer import cprint
from vodbot.util import format_duration, format_size

import os
import requests

from datetime import datetime
from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, wait
from functools import partial
from requests.exceptions import RequestException
from typing import List, Tuple
from pathlib import Path


class DownloadFailed(Exception):
	pass

class DownloadCancelled(Exception):
	pass


def _download(url: str, path: str, timeout:float, chunk_size:int) -> int:
	tmp_path = path + ".tmp"
	response = requests.get(url, stream=True, timeout=timeout)
	size = 0
	with open(tmp_path, 'wb') as target:
		for chunk in response.iter_content(chunk_size=chunk_size):
			target.write(chunk)
			size += len(chunk)

	os.rename(tmp_path, path)
	return size


def download_file(url:str, path:str, retries:int, timeout:int, chunk_size:int) -> Tuple[int, bool]:
	if os.path.exists(path):
		return os.path.getsize(path), True

	for _ in range(retries):
		try:
			return _download(url, path, timeout, chunk_size), False
		except RequestException:
			pass

	raise DownloadFailed()


def _print_progress(video_id: str, futures: List[Future]) -> None:
	downloaded_count = 0
	downloaded_size = 0
	existing_size = 0
	max_msg_size = 0
	start_time = datetime.now()
	total_count = len(futures)

	try:
		for future in as_completed(futures):
			(size, existed) = future.result()
			downloaded_count += 1
			downloaded_size += size
			if existed:
				existing_size += size

			percentage = 100 * downloaded_count / total_count
			est_total_size = total_count * downloaded_size / downloaded_count
			duration = (datetime.now() - start_time).seconds
			speed = (downloaded_size - existing_size) / duration if duration else 0
			remaining = (total_count - downloaded_count) * duration / downloaded_count

			msg = " ".join([
				f"#fM#lVOD#r `#fM{video_id}#r` pt#fC{downloaded_count}#r/#fB#l{total_count}#r,",
				f"#fC{format_size(downloaded_size, include_units=False)}#r/#fB#l{format_size(est_total_size)}#r"
				f"#d({percentage:.1f}%)#r;",
				f"at #fY~{format_size(speed)}/s#r;" if speed > 0 else "",
				f"#fG~{format_duration(remaining)}#r left" if speed > 0 else "",
			])

			max_msg_size = max(len(msg), max_msg_size)
			cprint("#c\r" + msg.ljust(max_msg_size), end="")
	except KeyboardInterrupt:
		_, not_done = wait(futures, timeout=0)
		for future in not_done:
			future.cancel()
		wait(not_done, timeout=None)
		raise DownloadCancelled()


def download_files(conf:Config, video_id:str, base_url:str, target_dir:Path, vod_paths:List[str]) -> OrderedDict[str, str]:
	urls = [base_url + path for path in vod_paths]
	targets = [str(target_dir / path) for path in vod_paths]
	retries = conf.pull.connection_retries
	timeout = conf.pull.connection_timeout
	chunk_size = conf.pull.chunk_size
	
	partials = (partial(download_file, url, path, retries, timeout, chunk_size)
		for url, path in zip(urls, targets))

	with ThreadPoolExecutor(max_workers=conf.pull.max_workers) as executor:
		futures = [executor.submit(fn) for fn in partials]
		_print_progress(video_id, futures)

	return OrderedDict(zip(vod_paths, targets))
