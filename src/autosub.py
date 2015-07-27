########################################################################
# autosub.py -- the entry point to autosub, initializes queues, starts
#       threads, and cleans up if autosub is stopped using SIGUSR2.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
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
####
# log_a_msg()
####
def log_a_msg(msg, loglevel):
      logger_queue.put(dict({"msg": msg, "type": loglevel, "loggername": "autosub.py"}))

####
#  connect_to_db()
####
def connect_to_db(dbname):
   # connect to sqlite database ...
   try:
      con = lite.connect(dbname)
   except:
      logmsg = "Failed to connect to database: " + dbname
      log_a_msg(logmsg, "ERROR")

   cur = con.cursor()
   return cur, con

####
#
####
def check_and_init_db_table(cur, con, tablename, fields):
   sqlcmd = "SELECT name FROM sqlite_master WHERE type == 'table' AND name = '" + tablename + "';"
   cur.execute(sqlcmd)
   res = cur.fetchall()
   if res:
      logmsg = 'table ' + tablename + ' exists'
      log_a_msg(logmsg, "DEBUG")
      #TODO: in this case, we might want to check if one entry per task is already there, and add new
      #      empty entries in case a task does not have one. This is only a problem, if the number of
      #      tasks in the config file is changed AFTER the TaskStats table has been changed!
      return 0
   else:
      logmsg = 'table ' + tablename + ' does not exist'
      log_a_msg(logmsg, "DEBUG")

      sqlcmd = "CREATE TABLE " + tablename + "(" + fields + ");"
      cur.execute(sqlcmd)
      con.commit()
      return 1

####
# init_deb_statvalue()
#
# Add entries for the statistics counters, and initialize them to 0.
####
def init_db_statvalue(cur, con, countername, value):
      sql_cmd="INSERT INTO StatCounters (CounterId, Name, value) VALUES(NULL, '" + countername + "', " + str(value) + ");"
      cur.execute(sql_cmd);
      con.commit();

def check_dir_mkdir(directory): 
   if not os.path.exists(directory):
      os.mkdir(directory)
      logmsg = "Created directory: " + directory
      log_a_msg(logmsg, "DEBUG")
   else:
      logmsg = "Directory already exists: " + directory
      log_a_msg(logmsg, "WARNING")

####
# set_general_config_param()
####
def set_general_config_param(cur, con, configitem, content):
     sql_cmd="INSERT INTO GeneralConfig (ConfigItem, Content) VALUES('" + configitem + "', '" + content + "');"
     cur.execute(sql_cmd);
     con.commit();


####
# load_specialmessage_to_db()
####
def load_specialmessage_to_db(cur, con, msgname, filename):
     with open (filename, "r") as smfp:
        data=smfp.read()
     smfp.close()
     sql_cmd="INSERT INTO SpecialMessages (EventName, EventText) VALUES('" + msgname + "', '" + data + "');"
     cur.execute(sql_cmd);
     con.commit();

####
# load_generalconfig_to_db()
####
def load_generalconfig_to_db(cur, con, configItem, content):
     sql_cmd="INSERT INTO GeneralConfig (ConfigItem, Content) VALUES('" + configItem + "', '" + content + "');"
     cur.execute(sql_cmd);
     con.commit();

####
# Check if all databases, tables, etc. are available, or if they have to be created.
# if non-existent --> create them
####
def init_ressources(numThreads, numTasks):
   cur,con = connect_to_db('semester.db') 

   ####################
   ####### Users ######
   ####################
   check_and_init_db_table(cur, con, "Users", "UserId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, email TEXT, first_mail INT, last_done INT, current_task INT")
   ####################
   ##### TaskStats ####
   ####################
   ret = check_and_init_db_table(cur, con, "TaskStats", "TaskId INTEGER PRIMARY KEY, nr_submissions INT, nr_successful INT")
   if ret:
      for t in range (1, numTasks+1):
         sql_cmd="INSERT INTO TaskStats (TaskId, nr_submissions, nr_successful) VALUES("+ str(t) + ", 0, 0);"
         cur.execute(sql_cmd);
      con.commit();
   ####################
   ### StatCounters ###
   ####################
   ret = check_and_init_db_table(cur, con, "StatCounters", "CounterId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, value INT")
   if ret:
      # add the stat counter entries and initialize them to 0:
      init_db_statvalue(cur, con, 'nr_mails_fetched', 0)
      init_db_statvalue(cur, con, 'nr_mails_sent', 0)
      init_db_statvalue(cur, con, 'nr_questions_received', 0)
   ####################
   ##### UserTasks ####
   ####################
   ret = check_and_init_db_table(cur, con, "UserTasks", "uniqeID INTEGER PRIMARY KEY AUTOINCREMENT, TaskNr INT, UserId INT, TaskParameters TEXT, TaskDescription TEXT, TaskAttachments TEXT")
   ####################
   # Directory users ##
   ####################
   check_dir_mkdir("users")
   con.close() # close here, since we re-open the databse in the while(True) loop


   cur,con = connect_to_db('course.db')

   ####################
   ## SpecialMessages #
   ####################
   ret = check_and_init_db_table(cur, con, "SpecialMessages", "EventName TEXT PRIMARY KEY, EventText TEXT")
   if ret: # that table did not exists, therefore we use the .txt files to initialize it!
      load_specialmessage_to_db(cur, con, 'WELCOME', 'SpecialMessages/welcome.txt')
      load_specialmessage_to_db(cur, con, 'USAGE', 'SpecialMessages/usage.txt')
      load_specialmessage_to_db(cur, con, 'QUESTION', 'SpecialMessages/question.txt')
      load_specialmessage_to_db(cur, con, 'INVALID', 'SpecialMessages/invalidtask.txt')
      load_specialmessage_to_db(cur, con, 'CONGRATS', 'SpecialMessages/congratulations.txt')
      load_specialmessage_to_db(cur, con, 'REGOVER', 'SpecialMessages/registrationover.txt')
   #####################
   # TaskConfiguration #
   #####################
   ret = check_and_init_db_table(cur, con, "TaskConfiguration", "TaskNr INT PRIMARY KEY, TaskStart INT, TaskDeadline INT, PathToTask TEXT, GeneratorExecutable TEXT, TestExecutable TEXT, Score INT, TaskOperator TEXT")
   ####################
   ### GeneralConfig ##
   ####################
   ret = check_and_init_db_table(cur, con, "GeneralConfig", "ConfigItem Text PRIMARY KEY, Content TEXT")
   #TODO: Find useful values to inizialize GeneralConfig
   #use load_generalconfig_to_db 

   ####################
   #### Whitelist #####
   ####################
   ret = check_and_init_db_table(cur, con, "Whitelist", "UniqeID INTEGER PRIMARY KEY AUTOINCREMENT, Email TEXT")


   #####################
   # Num workers,tasks #
   #####################
   if ret: # if that table did not exist, load the defaults given in the configuration file
      set_general_config_param(cur, con, 'num_workers', str(numThreads))
      set_general_config_param(cur, con, 'num_tasks', str(numTasks))
   con.close()


########################################
threadID = 1
worker_t = []
exit_flag = 0

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
queueSize = config.getint('general', 'queue_size')
poll_period = config.getint('general', 'poll_period')

job_queue = queue.Queue(queueSize)
sender_queue = queue.Queue(queueSize)
logger_queue = queue.Queue(queueSize)
gen_queue = queue.Queue(queueSize)

#Before we do anything else: start the logger thread, so we can log whats going on
logger_t = logger.autosubLogger(threadID, "logger", logger_queue)#, logging.DEBUG)
logger_t.daemon = True # make the logger thread a daemon, this way the main
                       # will clean it up before terminating!
logger_t.start()
threadID += 1

signal.signal(signal.SIGUSR1, sig_handler)

init_ressources(numThreads, numTasks)

sender_t = sender.mailSender(threadID, "sender", sender_queue, autosub_mail, autosub_user, autosub_passwd, smtpserver, logger_queue, numTasks)
sender_t.daemon = True # make the sender thread a daemon, this way the main
                       # will clean it up before terminating!
sender_t.start()
threadID += 1

fetcher_t = fetcher.mailFetcher(threadID, "fetcher", job_queue, sender_queue, gen_queue, autosub_user, autosub_passwd, imapserver, logger_queue, numTasks, poll_period)
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
