#!/usr/bin/python

from subprocess import Popen, PIPE, STDOUT
import pty
import os

master, slave = pty.openpty()

p1 = Popen(['./command.py'], shell=True, stdin = slave, stdout = slave, 
       stderr=slave, close_fds=True)

p2 = Popen(['./receive-file.py'], shell=True, stdin = slave, stdout = slave, 
       stderr=slave, close_fds=True)
stdout = os.fdopen(master)

while True:
  l = stdout.readline()
  print l,


