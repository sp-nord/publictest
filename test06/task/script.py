import os
import time
import shutil
import fire


def cur_size(directory: str = '.'):
    """
    :param directory: str, default: '.'. Directory to check
    :return: Size of all files in bytes in current directory only
    """
    size = sum(os.path.getsize(os.path.join(directory, f)) for f in os.listdir(directory)
               if os.path.isfile(os.path.join(directory, f)))
    return size


def total_size(directory: str = '.'):
    """
    :param directory: str, default: '.'. Directory to check
    :return: Size of all files in bytes in directory and subdirectories
    """
    size = cur_size(directory)
    size += sum(total_size(os.path.join(directory, d)) for d in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, d)))
    return size


def old_files(directory: str = '.', days: int = 90):
    """
    :param directory: str, default: '.'. Directory to check
    :param days: int, default: 90. Age threshold
    :return: List of files older than given age in current directory
    """
    age = days * 24 * 60 * 60
    now = time.time()
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if (os.path.isfile(os.path.join(directory, f))
                and os.path.getmtime(os.path.join(directory, f)) < now - age)]


def total_old_files(directory: str = '.', days: int = 90):
    """
    :param directory: str, default: '.'. Directory to check
    :param days: int, default: 90. Age threshold
    :return: List of files older than given age including subdirectories
    """
    res = old_files(directory, days)
    for d in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, d)):
            res += total_old_files(os.path.join(directory, d))
    return res


def disk_free(path: str = '.'):
    """
    :param path: str, default: '.'. Disk is checked based on path given
    :return: Free space on disk in bytes
    """
    return shutil.disk_usage(path).free


def remove(files: list, dry: bool = False):
    """
    Removes files given in a list
    :param files: list. List of files to be removed
    :param dry: bool, default = False. Dry run
    :return: Number of files removed
    """
    count = 0
    for fp in files:
        print('removing {}'.format(fp))
        if not dry:
            os.unlink(fp)
        count += 1
    return count


def run(directory: str = '.', days: int = 90, dir_mb: int = 1024, space_mb: int = 1024,
        recursive: bool = True, dry: bool = False):
    """
    :param directory: str, default: '.'. Directory to check
    :param days: int, default: 90. Maximum age of files to be removed in days
    :param dir_mb: int, default: 1024. Maximum directory size in megabytes
    :param space_mb: int, default: 1024. Minimum space disk in megabytes
    :param recursive: bool, default: True. Check directory recursively
    :param dry: bool, default: False. Dry run
    :return: Nothing
    """
    count = 0
    if disk_free(directory) / 1024 / 1024 < space_mb:
        if recursive and total_size(directory) / 1024 / 1024 > dir_mb:
            count = remove(total_old_files(directory, days), dry)
        elif cur_size(directory) / 1024 / 1024 > dir_mb:
            count = remove(old_files(directory, days), dry)
    print('{} files removed'.format(count))


if __name__ == '__main__':
    fire.Fire(run)
