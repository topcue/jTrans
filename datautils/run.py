import os
import subprocess
import multiprocessing
import time
from util.pairdata import pairdata

#! $ mkdir -p /mnt/c/Users/user/workspace
#! $ ln -s /mnt/c/Users/user/workspace /home/user/win_workspace
WSL_PREFIX = "/home/user/win_workspace"
WIN_PREFIX = "C:/Users/user/workspace"

def wsl_to_win_path(p):
	if p == WSL_PREFIX or p.startswith(WSL_PREFIX + "/"):
		return WIN_PREFIX + p[len(WSL_PREFIX):]
	return p

def win_to_wsl_path(p):
	if p == WIN_PREFIX or p.startswith(WIN_PREFIX + "/"):
		return WSL_PREFIX + p[len(WIN_PREFIX):]
	return p


IDA_PATH = "/mnt/c/Users/user/workspace/IDA/idat64.exe"

BASE_PATH = "/home/user/win_workspace/storage/jtrans"

DATA_ROOT = os.path.join(BASE_PATH, "dataset")
STRIP_PATH = os.path.join(BASE_PATH, "dataset_strip")

cur_script_dir_path = os.path.dirname(os.path.abspath(__file__))
IDA_SCRIPT_PATH = os.path.join(cur_script_dir_path, "process.py")

LOG_PATH = "log"
IDB_PATH = os.path.join(BASE_PATH, "idb")
SAVE_ROOT = os.path.join(BASE_PATH, "extract")

NUM_JOBS = 24


def getTarget(path):
	target = []
	for root, _, files in os.walk(path):
		for file in files:
			target.append(os.path.join(root, file))
	return target


def run_ida(cmd, out_path=None, err_path=None, debug=False):
	if debug:
		with open(out_path, "wb") as out_f, open(err_path, "wb") as err_f:
			return subprocess.call(cmd, stdout=out_f, stderr=err_f)
	else:
		# Discard stdout/stderr
		return subprocess.call(
			cmd,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)


def strip_one(target_path: str) -> tuple[str, str, int]:
	filename = os.path.basename(target_path)
	stripped_path = os.path.join(STRIP_PATH, filename + ".strip")

	# Use subprocess to get a real return code
	# strip -s <in> -o <out>
	cmd_strip = f"strip -s {target_path} -o {stripped_path}"
	ret = subprocess.call(cmd_strip.split(' '))
	return (target_path, stripped_path, ret)


def strip_all_parallel(target_list, num_jobs: int):
	results = []
	with multiprocessing.Pool(processes=num_jobs) as pool:
		for orig, stripped, ret in pool.imap_unordered(strip_one, target_list, chunksize=16):
			if ret != 0:
				# If you want strict failure, raise instead.
				# raise RuntimeError(f"strip failed: {orig} (ret={ret})")
				print(f"[WARN] strip failed: {orig} (ret={ret})")
				continue
			results.append(stripped)
	return results


def main():
	DEBUG = False

	os.makedirs(STRIP_PATH, exist_ok=True)
	os.makedirs(IDB_PATH,   exist_ok=True)
	os.makedirs(LOG_PATH,   exist_ok=True)
	os.makedirs(SAVE_ROOT, exist_ok=True)

	start = time.time()

	target_list = getTarget(DATA_ROOT)

	# Stage 1) strip in parallel
	stripped_list = strip_all_parallel(target_list, num_jobs=NUM_JOBS)

	# Stage 2) run IDA in parallel on stripped files
	pool = multiprocessing.Pool(processes=NUM_JOBS)
	for ida_input in stripped_list:
		filename_strip = os.path.basename(ida_input)          # e.g., xxx.strip
		filename = filename_strip.replace(".strip", "")       # e.g., xxx

		ida_input_win = wsl_to_win_path(ida_input)
		IDB_PATH_WIN = wsl_to_win_path(IDB_PATH)

		cmd_str = (
			f"{IDA_PATH} -L{LOG_PATH}/{filename}.log "
			f"-c -A -S{IDA_SCRIPT_PATH} "
			f"-o{IDB_PATH_WIN}/{filename}.idb {ida_input_win}"
		)
		cmd = cmd_str.split(" ")

		out_path = os.path.join(LOG_PATH, f"{filename}.ida.stdout.txt")
		err_path = os.path.join(LOG_PATH, f"{filename}.ida.stderr.txt")

		pool.apply_async(run_ida, args=(cmd, out_path, err_path, DEBUG))
	pool.close()
	pool.join()

	print("[*] Features Extracting Done")
	print("[*] Saving..")
	pairdata(SAVE_ROOT)

	end = time.time()
	print(f"[*] Time Cost: {end - start} seconds")

if __name__ == "__main__":
	main()

# EOF
