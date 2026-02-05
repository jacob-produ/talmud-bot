import os
import time
import hashlib

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
DONE_DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "done")


def allow_download_files_from_server(driver):
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': DOWNLOAD_DIR}}
    driver.execute("send_command", params)


def get_last_downloaded_file():
    files = []
    while not files:
        files = [os.path.join(DOWNLOAD_DIR, file) for file in os.listdir(DOWNLOAD_DIR)
                 if os.path.isfile(os.path.join(DOWNLOAD_DIR, file)) and not file.endswith("crdownload") and not file.endswith(".tmp")]
        time.sleep(1)

    return max(files, key=os.path.getctime)


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


def create_downloads_dir():
    create_dir(DOWNLOAD_DIR)
    create_dir(DONE_DOWNLOAD_DIR)


def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    print(get_last_downloaded_file(r"D:\temp"))

