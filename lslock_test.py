import os
import fcntl
import multiprocessing
import subprocess
import time
import sys
import ast

DIRECTORY = '/tmp/lslock-test'


def make_dir(directory):
    """
    Helper function to create /tmp/lslock-test
    :param directory: string
    :return:
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_file(dirpath, fname, content):
    """
    Helper function to populate the /tmp/lslock-test directory
    with files
    :param dirpath: string
    :param fname: string
    :param content: string
    :return:
    """
    file_path = os.path.join(dirpath, fname)
    if not os.path.isfile(file_path):
        os.makedirs(dirpath)
        with open(os.path.join(dirpath, fname), 'w') as fh:
            fh.write(content)


def get_file_name(num):
    """
    Helper function to create the filename based on an index. Returns
    the concatenation as a string.
    :param num: integer
    :return: fname: string
    """
    fname = 'file' + str(num)
    return fname


def setup():
    """
    Umbrella function to setup the files and the directory.
    :return:
    """
    make_dir(DIRECTORY)
    for i in range(5):
        content = get_file_name(i)
        jobdir = os.path.join(DIRECTORY, content)
        write_file(jobdir, content + '.lock', content)


def child(fpath):
    """
    Function that forks a child process. The pid is 0 in the child
    and in the parent it is the pid of the child. So in the child we
    sys.exit to prevent the child from continuing on with its copy
    of the script.
    :param fpath: string
    :return: pid: integer
    """
    pid = os.fork()
    if pid == 0:
        with open(fpath, 'r') as f_h:
            fcntl.flock(f_h, fcntl.LOCK_SH | fcntl.LOCK_NB)
            time.sleep(3)
            sys.exit(0)
    else:
        return pid


def process_task(message):
    """
    This is the function that the pool workers call when their process
    is spawned. message is a tuple that encapsulates the behavior we want
    out of the function.

    If the tuple is of the form (int, bool) then
    it creates a lock on a file based on the integer. If the bool is false
    it doesn't spawn a child. If the bool is true, then it spawns a child.
    If the tuple is of the form ('lslock', bool) then it spawns
    a subprocess and runs lslock.py and captures its output and returns it.
    :param message: tuple
    :return: tuple, or dict
    """
    f_num = message[0]
    spawn_child = message[1]
    if f_num.isdigit():
        f_n = get_file_name(f_num)
        f_name = f_n + '.lock'
        job_path = os.path.join(DIRECTORY, f_n)
        f_path = os.path.join(job_path, f_name)
        with open(f_path, 'r') as fd:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            pids = [str(os.getpid())]
            if spawn_child:
                ch_pid = child(f_path)
                pids.append(str(ch_pid))
            if not spawn_child:
                time.sleep(3)
        return f_name, pids

    elif f_num == 'lslock':
        time.sleep(1)
        cmd = ['python3', 'lslock.py', '-p', DIRECTORY]
        res = subprocess.check_output(cmd)
        res = res.decode('ascii')
        return ast.literal_eval(res)


def compare_dicts(fixd, testd):
    """
    Helper function to compare dictionaries for the fixtures and
    the results from lslock. Called twice with args switched
    :param fixd: dict
    :param testd: dict
    :return: bool
    """
    flag = True
    for key in fixd:
        if key in testd:
            if set(fixd[key]) == set(testd[key]):
                continue
            else:
                flag = False
                break
        else:
            flag = False
            break
    return flag


def main():
    setup()

    inputs = [('0', False), ('1', False), ('2', False), ('3', False), ('4', True), ('lslock', True)]
    pool_size = 6
    pool = multiprocessing.Pool(processes=pool_size, maxtasksperchild=1)

    results = pool.map(process_task, inputs)
    pool.close()
    pool.join()

    fixtures_dict = {key: val for key, val in results[:-1]}
    test_dict = results[-1]

    check = compare_dicts(fixtures_dict, test_dict) and compare_dicts(test_dict, fixtures_dict)

    print("lslock found all locks: ", check)


if __name__ == "__main__":
    main()
