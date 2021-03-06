import sys
import stat
import os
import argparse


def get_extension(path):
    """
     Helper function to grab the extension of a file from its path
    :param path: string
    :return: file_ext: string
    """
    filename, file_ext = os.path.splitext(path)
    return file_ext[1:]


def walktree(top):
    """
    Wrapper around os.walk to go through a directory tree and grab
    all *.lock files and put them in a dictionary
    :param top: string
    :return: list_of_files: dictionary
    """
    list_of_files = {}
    for (dirpath, dirnames, filenames) in os.walk(top):
        for filename in filenames:
            if filename.endswith('.lock'):
                list_of_files[filename] = os.stat(os.path.join(dirpath, filename)).st_ino
    return list_of_files


def get_inode_and_pid(line):
    """
    Helper function to grab the inode and pid from a line taken
    from /proc/locks
    :param line: string
    :return: inode, pid: string, string
    """
    spl_line = line.split(' ')
    spl_line = [x for x in spl_line if x]
    pid = spl_line[4]
    inode = spl_line[5].split(':')[-1]
    return inode, pid


def get_pids_and_inodes():
    """
    Function to get the inodes and pids for each entry in /proc/locks
    :return: inode_and_pid: dictionary where key is inode and value is pid
    """
    with open('/proc/locks', 'r') as proc_f:
        inode_and_pid = {}
        for line in proc_f:
            inode, pid = get_inode_and_pid(line)
            if inode in inode_and_pid:
                inode_and_pid[inode].append(pid)
            else:
                inode_and_pid[inode] = [pid]

    return inode_and_pid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', dest='path', required=True)
    args = parser.parse_args()

    path_and_inode = walktree(args.path)
    inode_and_pid = get_pids_and_inodes()
    path_and_pid = {}
    for key in path_and_inode.keys():
        inode = path_and_inode[key]
        inode = str(inode)
        if inode_and_pid.get(inode, False):
            path_and_pid[key] = inode_and_pid[inode]

    print(path_and_pid)


if __name__ == '__main__':
    main()
