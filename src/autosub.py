########################################################################
# autosub.py -- the entry point to autosub, initializes queues, starts
#       threads, and cleans up if autosub is stopped using SIGUSR2.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading, queue
import email, getpass, imaplib, os, time
import sqlite3 as lite
import fetcher, worker, sender, logger, generator
import optparse
import signal
import logging
import configparser

def sig_handler(signum, frame):
   logger_queue.put(dict({"msg": "Shutting down autosub...", "type": "INFO", "loggername": "Main"}))
   exit_flag = 1

########################################
threadID = 1
worker_t = []
exit_flag = 0

job_queue = queue.Queue(200)
sender_queue = queue.Queue(200)
logger_queue = queue.Queue(200)
gen_queue = queue.Queue(200)

#Before we do anything else: start the logger thread, so we can log whats going on
logger_t = logger.autosubLogger(threadID, "logger", logger_queue)#, logging.DEBUG)
logger_t.daemon = True # make the fetcher thread a daemon, this way the main
                       # will clean it up before terminating!
logger_t.start()
threadID += 1

parser = optparse.OptionParser()
parser.add_option("-c", "--config-file", dest="configfile", type="string",
           help=("The config file used for this instance of autosub."))

parser.set_defaults(configfile="default.cfg")
opts, args = parser.parse_args()

config = configparser.ConfigParser()
config.readfp(open(opts.configfile))
imapserver = config.get('imapserver', 'servername')
autosub_user = config.get('imapserver', 'username')
autosub_passwd = config.get('imapserver', 'password')
autosub_mail = config.get('imapserver', 'email')
smtpserver = config.get('smtpserver', 'servername')
numThreads = config.getint('general', 'num_workers')
numTasks = config.getint('challenge', 'num_tasks')

signal.signal(signal.SIGUSR1, sig_handler)

sender_t = sender.mailSender(threadID, "sender", sender_queue, autosub_mail, autosub_user, autosub_passwd, smtpserver, logger_queue, numTasks)
sender_t.daemon = True # make the sender thread a daemon, this way the main
                       # will clean it up before terminating!
sender_t.start()
threadID += 1

fetcher_t = fetcher.mailFetcher(threadID, "fetcher", job_queue, sender_queue, gen_queue, autosub_user, autosub_passwd, imapserver, logger_queue, numTasks)
fetcher_t.daemon = True # make the fetcher thread a daemon, this way the main
                        # will clean it up before terminating!
fetcher_t.start()
threadID += 1

generator_t = generator.taskGenerator(threadID, "generator", gen_queue, sender_queue, logger_queue)
generator_t.daemon = True # make the fetcher thread a daemon, this way the main
                          # will clean it up before terminating!
generator_t.start()
threadID += 1

msg_config = "Used config-file: " + opts.configfile
logger_queue.put(dict({"msg": msg_config, "type": "INFO", "loggername": "Main"}))
#Next we start a couple of worker threads:

while (threadID <= numThreads + 3):
   tName = "Worker" + str(threadID-3)
   t = worker.worker(threadID, tName, job_queue, sender_queue, logger_queue)
   t.daemon = True
   t.start()
   worker_t.append(t)
   threadID += 1

   logger_queue.put(dict({"msg": "All threads started successfully", "type": "INFO", "loggername": "Main"}))

while (not exit_flag):
   time.sleep(100)

time.sleep(1) # give the logger thread a little time write the last log message 
