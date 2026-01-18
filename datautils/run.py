import os
import subprocess
import multiprocessing
import time
from util.pairdata import pairdata


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

#! WSL: pip install networkx tqdm
def main():
	DEBUG = False

	start = time.time()
	target_list = getTarget(DATA_ROOT)

	os.system(f"mkdir -p {STRIP_PATH} {IDB_PATH} {LOG_PATH} {SAVE_ROOT}")

	pool = multiprocessing.Pool(processes=8)
	for target in target_list:
		filename = target.split('/')[-1]
		filename_strip = filename + '.strip'
		ida_input = os.path.join(STRIP_PATH, filename_strip)

		if DEBUG:
			print(f"[DEBUG] filename: {filename}")
			print(f"[DEBUG] ida_input: {ida_input}")

		cmd_strip = f"strip -s {target} -o {ida_input}"
		os.system(cmd_strip)

		ida_input_win = wsl_to_win_path(ida_input)
		IDB_PATH_WIN = wsl_to_win_path(IDB_PATH)

		cmd_str = f"{IDA_PATH} -L{LOG_PATH}/{filename}.log -c -A -S{IDA_SCRIPT_PATH} -o{IDB_PATH_WIN}/{filename}.idb {ida_input_win}"
		cmd = cmd_str.split(' ')

		if DEBUG:
			print(f"[DEBUG] cmd_str: {cmd_str}")

		#! For debug
		out_path = os.path.join(LOG_PATH, f"{filename}.ida.stdout.txt")
		err_path = os.path.join(LOG_PATH, f"{filename}.ida.stderr.txt")

		# os.system(cmd_str)
		pool.apply_async(run_ida, args=(cmd, out_path, err_path))
	pool.close()
	pool.join()
	print("[*] Features Extracting Done")

	print("[*] Saving..")
	pairdata(SAVE_ROOT)

	end = time.time()
	print(f"[*] Time Cost: {end - start} seconds")


if __name__ == '__main__':
	main()

# EOF
