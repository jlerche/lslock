import os
import fcntl
import multiprocessing
import subprocess
import time
import sys
import ast

DIRECTORY = '/tmp/lslock-test'

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_file(dirpath, fname, content):
    file_path = os.path.join(dirpath, fname)
    if not os.path.isfile(file_path):
        os.makedirs(dirpath)
        with open(os.path.join(dirpath, fname), 'w') as fh:
            fh.write(content)

def get_file_name(num):
    fname = 'file' + str(num)
    return fname

def setup():
    make_dir(DIRECTORY)
    for i in range(5):
        content = get_file_name(i)
        jobdir = os.path.join(DIRECTORY, content)
        write_file(jobdir, content + '.lock', content)

def child(fpath):
    pid = os.fork()
    if pid == 0:
        with open(fpath, 'r') as f_h:
            fcntl.flock(f_h, fcntl.LOCK_SH | fcntl.LOCK_NB)
            time.sleep(3)
            sys.exit(0)
    else:
        return pid


def process_task(message):
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
        return (f_name, pids)

    elif f_num == 'lslock':
        time.sleep(1)
        cmd = ['python3', 'lslock.py', '-p', DIRECTORY]
        res = subprocess.check_output(cmd)
        res =res.decode('ascii')
        return ast.literal_eval(res)

def compare_dicts(fixd, testd):
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

    inputs = [('0', False), ('1', False), ('2', False), ('3',False), ('4', True), ('lslock', True)]
    pool_size = 6
    pool = multiprocessing.Pool(processes=pool_size, maxtasksperchild=1)

    results = pool.map(process_task, inputs)
    pool.close()
    pool.join()

    fixtures_dict = {key: val for key,val in results[:-1]}
    test_dict = results[-1]

    print("lslock found all locks: ", compare_dicts(fixtures_dict, test_dict))



if __name__ == "__main__":
    main()
