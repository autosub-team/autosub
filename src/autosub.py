########################################################################
# autosub.py -- the entry point to autosub, initializes queues, starts
#               threads, and cleans up if autosub is stopped using SIGUSR2.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck    <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import queue

import getpass
import time

import optparse
import signal
import logging
import configparser

import common as c
import fetcher
import worker
import sender
import logger
import generator
import activator
import dailystats

####
# sig_handler
####
def sig_handler(signum, frame):
    """
    Signal Handler to manage shutdown of autosub.
    """

    logger_queue.put(dict({"msg": "Shutting down autosub...", "type": "INFO", \
                           "loggername": "Main"}))
    ret_exit = 1

    return ret_exit


####
#    check_and_init_db_table
####
def check_and_init_db_table(dbname, tablename, fields):
    """
    Check if a table exists, if not create it with fields.
    """

    cur, con = c.connect_to_db(dbname, logger_queue, "autosub.py")

    data = {'name': tablename}
    sql_cmd = "SELECT name FROM sqlite_master WHERE type == 'table' AND name = :name"
    cur.execute(sql_cmd, data)
    res = cur.fetchall()

    if res:
        logmsg = 'table ' + tablename + ' exists'
        c.log_a_msg(logger_queue, "autosub.py", logmsg, "DEBUG")
        #TODO: in this case, we might want to check if one entry per task is already
        # there, and add new empty entries in case a task does not have one. This is only
        # a problem, if the number of tasks in the config file is changed AFTER the
        # TaskStats table has been changed!

        con.close()

        return 0
    else:
        logmsg = 'table ' + tablename + ' does not exist'
        c.log_a_msg(logger_queue, "autosub.py", logmsg, "DEBUG")

        data = {'fields': fields}
        sql_cmd = "CREATE TABLE {0}(:fields)".format(tablename)
        cur.execute(sql_cmd, data)
        con.commit()

        con.close()

        return 1

####
# init_db_statvalue()
# ####
def init_db_statvalue(semesterdb, countername, value):
    """
    Add entries for the statistics counters, and initialize them to 0.
    """

    curs, cons = c.connect_to_db(semesterdb, logger_queue, "autosub.py")

    data = {'Name': countername, 'Value': str(value)}
    sql_cmd = ("INSERT INTO StatCounters (CounterId, Name, Value) "
               "VALUES(NULL, :Name, :Value)")
    curs.execute(sql_cmd, data)
    cons.commit()

    cons.close()

####
# set_general_config_param
####
def set_general_config_param(coursedb, configitem, content):
    """
    Set a general config parameter in the database.
    """

    curc, conc = c.connect_to_db(coursedb, logger_queue, "autosub.py")

    data = {'ConfigItem' : configitem, 'Content': content}
    sql_cmd = ("INSERT INTO GeneralConfig (ConfigItem, Content) "
               "VALUES(:ConfigItem, :Content)")
    curc.execute(sql_cmd, data)
    conc.commit()

    conc.close()

####
# load_specialmessage_to_db
####
def load_specialmessage_to_db(coursedb, msgname, filename, subsmission_email, course_name):
    """
    Load the SpecialMessages in the db.
    """

    curc, conc = c.connect_to_db(coursedb, logger_queue, "autosub.py")

    with open(filename, "r") as smfp:
        filecontent = smfp.read()

        filecontent = filecontent.replace("<SUBMISSIONEMAIL>", \
                                          "<" + subsmission_email + ">")
        filecontent = filecontent.replace("<COURSENAME>", course_name)

        data = {'EventName': msgname, 'EventText': filecontent}
        sql_cmd = ("INSERT INTO SpecialMessages (EventName, EventText) "
                   "VALUES(:EventName, :EventText)")
        curc.execute(sql_cmd, data)
        conc.commit()

        conc.close()

####
# init_ressources
####
def init_ressources(semesterdb, coursedb, num_tasks, subsmission_email, challenge_mode, \
                    course_name):
    """
    Check if all databases, tables, etc. are available, or if they have to be created.
    If non-existent --> create them.
    """

    # needed for some actions after table creation
    curs, cons = c.connect_to_db(semesterdb, logger_queue, "autosub.py")

    ####################
    ####### Users ######
    ####################
    fields = ("UserId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Email TEXT, "
              "FirstMail DATETIME, LastDone DATETIME, CurrentTask INT")
    check_and_init_db_table(semesterdb, "Users", fields)

    ####################
    ##### TaskStats ####
    ####################
    fields = "TaskId INTEGER PRIMARY KEY, NrSubmissions INT, NrSuccessful INT"
    ret = check_and_init_db_table(semesterdb, "TaskStats", fields)
    if ret:
        for t in range(1, num_tasks + 1):
            data = {'TaskId': t}
            sql_cmd = ("INSERT INTO TaskStats (TaskId, NrSubmissions, NrSuccessful) "
                       "VALUES(:TaskID, 0, 0)")
            curs.execute(sql_cmd, data)
        cons.commit()

    ####################
    ### StatCounters ###
    ####################
    fields = "CounterId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Value INT"
    ret = check_and_init_db_table(semesterdb, "StatCounters", fields)
    if ret:
        # add the stat counter entries and initialize them to 0:
        init_db_statvalue(semesterdb, 'nr_mails_fetched', 0)
        init_db_statvalue(semesterdb, 'nr_mails_sent', 0)
        init_db_statvalue(semesterdb, 'nr_questions_received', 0)
        init_db_statvalue(semesterdb, 'nr_non_registered', 0)
        init_db_statvalue(semesterdb, 'nr_status_requests', 0)

    ####################
    ##### UserTasks ####
    ####################
    fields = ("UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, TaskNr INT, UserId INT, "
              "TaskParameters TEXT, TaskDescription TEXT, TaskAttachments TEXT, "
              "NrSubmissions INTEGER, FirstSuccessful INTEGER")
    ret = check_and_init_db_table(semesterdb, "UserTasks", fields)

    ####################
    #### Whitelist #####
    ####################
    fields = "UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, Email TEXT"
    ret = check_and_init_db_table(semesterdb, "Whitelist", fields)

    ####################
    # Directory users ##
    ####################
    c.check_dir_mkdir("users", logger_queue, "autosub.py")

    # we don't need semesterdb connection anymore
    cons.close()

    ####################
    ## SpecialMessages #
    ####################
    fields = "EventName TEXT PRIMARY KEY, EventText TEXT"
    ret = check_and_init_db_table(coursedb, "SpecialMessages", fields)

    # that table did not exists, therefore we use the .txt files to initialize it!
    if ret:
        filename = '{0}SpecialMessages/welcome.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'WELCOME', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/usage.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'USAGE', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/question.txt'.format(specialpath)

        load_specialmessage_to_db(coursedb, 'QUESTION', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/invalidtask.txt'.format(specialpath),
        load_specialmessage_to_db(coursedb, 'INVALID', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/congratulations.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'CONGRATS', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/registrationover.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'REGOVER', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/notallowed.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'NOTALLOWED', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/curlast.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'CURLAST', filename, subsmission_email, \
                                  course_name)

        filename = '{0}SpecialMessages/deadtask.txt'.format(specialpath)
        load_specialmessage_to_db(coursedb, 'DEADTASK', filename, subsmission_email, \
                                  course_name)

    #####################
    # TaskConfiguration #
    #####################
    fields = ("TaskNr INT PRIMARY KEY, TaskStart DATETIME, TaskDeadline DATETIME, "
              "PathToTask TEXT, GeneratorExecutable TEXT, TestExecutable TEXT, "
              "Score INT, TaskOperator TEXT, TaskActive BOOLEAN")
    ret = check_and_init_db_table(coursedb, "TaskConfiguration", fields)

    ####################
    ### GeneralConfig ##
    ####################
    fields = "ConfigItem Text PRIMARY KEY, Content TEXT"
    ret = check_and_init_db_table(coursedb, "GeneralConfig", fields)

    #####################
    # Num workers,tasks #
    #####################
    # if that table did not exist, load the defaults given in the configuration file
    if ret:
        set_general_config_param(coursedb, 'num_tasks', str(num_tasks))
        set_general_config_param(coursedb, 'registration_deadline', 'NULL')
        set_general_config_param(coursedb, 'archive_dir', 'archive/')
        set_general_config_param(coursedb, 'admin_email', '')
        set_general_config_param(coursedb, 'challenge_mode', challenge_mode)
        set_general_config_param(coursedb, 'course_name', course_name)


########################################
if __name__ == '__main__':
    """
    Main function for autosub. Parse config file, generate queues, init all tables,
    start threads
    """

    thread_id = 1
    worker_t = []
    exit_flag = 0


    ####################
    # Parse Configfile #
    ####################
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config-file", dest="configfile", type="string", \
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
    queue_size = config.getint('general', 'queue_size')

    try:
        challenge_mode = config.get('challenge', 'mode')
    except:
        challenge_mode = "normal"

    try:
        poll_period = config.getint('general', 'poll_period')
    except:
        poll_period = 60

    try:
        semesterdb = config.get('general', 'semesterdb')
    except:
        semesterdb = 'semester.db'

    try:
        coursedb = config.get('general', 'coursedb')
    except:
        coursedb = 'course.db'

    try:
        specialpath = config.get('general', 'specialpath')
    except:
        specialpath = ''

    try:
        course_name = config.get('general', 'course_name')
    except:
        course_name = 'No name set'

    try:
        logfile = config.get('general', 'logfile')
    except:
        logfile = '/tmp/autosub.log'


    num_tasks = config.getint('challenge', 'num_tasks')

    ####################
    # Generate Queues  #
    ####################
    job_queue = queue.Queue(queue_size)
    sender_queue = queue.Queue(queue_size)
    logger_queue = queue.Queue(queue_size)
    gen_queue = queue.Queue(queue_size)
    arch_queue = queue.Queue(queue_size)

    ####################
    ### Start Logger ###
    ####################

    #Before we do anything else: start the logger thread, so we can log whats going on
    logger_t = logger.autosubLogger(thread_id, "logger", logger_queue, logfile)

    # make the logger thread a daemon, this way the main will clean it up before
    # terminating!
    logger_t.daemon = True
    logger_t.start()
    thread_id += 1

    signal.signal(signal.SIGUSR1, sig_handler)

    ####################
    # Init Ressources  #
    ####################
    init_ressources(coursedb, semesterdb, num_tasks, autosub_mail, challenge_mode, \
                    course_name)

    ####################
    ## Start Threads  ##
    ####################
    sender_t = sender.mailSender(thread_id, "sender", sender_queue, autosub_mail, \
                                 autosub_user, autosub_passwd, smtpserver, logger_queue, \
                                 arch_queue, coursedb, semesterdb)

    # make the sender thread a daemon, this way the main will clean it up before
    # terminating!
    sender_t.daemon = True
    sender_t.start()
    thread_id += 1

    fetcher_t = fetcher.mailFetcher(thread_id, "fetcher", job_queue, sender_queue, \
                                    gen_queue, autosub_user, autosub_passwd, imapserver, \
                                    logger_queue, arch_queue, poll_period, coursedb, \
                                    semesterdb)

    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    fetcher_t.daemon = True
    fetcher_t.start()
    thread_id += 1

    generator_t = generator.taskGenerator(thread_id, "generator", gen_queue, \
                                          sender_queue, logger_queue, coursedb, \
                                          autosub_mail)

    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    generator_t.daemon = True
    generator_t.start()
    thread_id += 1

    activator_t = activator.taskActivator(thread_id, "activator", gen_queue, \
                                          sender_queue, logger_queue, coursedb, \
                                          semesterdb)

    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    activator_t.daemon = True
    activator_t.start()
    thread_id += 1

    msg_config = "Used config-file: " + opts.configfile
    logger_queue.put(dict({"msg": msg_config, "type": "INFO", "loggername": "Main"}))

    #Next start a couple of worker threads
    while thread_id <= numThreads + 5:
        tName = "Worker" + str(thread_id - 5)
        t = worker.worker(thread_id, tName, job_queue, gen_queue, sender_queue, \
                          logger_queue, coursedb, semesterdb)
        t.daemon = True
        t.start()
        worker_t.append(t)
        thread_id += 1

        logger_queue.put(dict({"msg": "All threads started successfully", \
                               "type": "INFO", "loggername": "Main"}))


    dailystats_t = dailystats.dailystatsTask(thread_id, "dailystats", logger_queue, \
                                             semesterdb)
    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    dailystats_t.daemon = True
    dailystats_t.start()

    while not exit_flag:
        time.sleep(100)

    # give the logger thread a little time write the last log message
    time.sleep(1)
