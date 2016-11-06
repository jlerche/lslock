# lslock
A utility to query a directory for *.lock files

## Usage
```
python3 lslock.py -p /tmp/lslock-test
```
It will print a dictionary to the terminal with the files and pids it fond.
## Tests
### lslock-test.py
```
python3 lslock-test.py
```
It will create 5 files and spawn 5 processes with one of them forking another and passing it the same file for 6 total locks.
At the end it will print whether `lslock.py` found them all.
### Unit tests
To run the unit tests
```
python3 -m unittest discover tests
```
