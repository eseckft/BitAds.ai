import hashlib
import os


def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_md5_for_files_in_folders(folders):
    _md5 = ""
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                md5_hash = md5(file_path)
                _md5 += md5_hash

    hash_md5 = hashlib.md5()
    hash_md5.update(_md5.encode("utf-8"))
    return hash_md5.hexdigest()
