########################################################################
# autosub.py -- the entry point to autosub, initializes queues, starts
#               threads, and cleans up if autosub is stopped using SIGUSR1.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

########################
#       LIBRARIES      #
########################

# python libraries
import sys
import queue
import time
import signal
import optparse
import configparser
import os

from jinja2 import FileSystemLoader, Environment

# autosub common functions
import common as c

# autosub thread classes
import fetcher
import worker
import sender
import logger
import generator
import activator
import dailystats

########################
#    GLOBAL VARIABLES  #
########################
# yes, global is bad, but with this each function has easy access to
# all the variables parsed from the config file and it is a nice overview here

imapserver = None
imapuser = None
imappasswd = None
imapmail = None
imapsecurity = None
imapport = None

smtpserver = None
smtpuser = None
smtppasswd = None
smtpmail = None
smtpsecurity = None
smtpport = None

num_workers = None
poll_period = None
semesterdb = None
coursedb = None
log_dir = None
log_threshhold = None
server_timeout = None
mail_retries = None

course_name = None
course_mode = None
tasks_dir = None
specialmsgs_dir = None
auto_advance = None
allow_requests = None

job_queue = None
sender_queue = None
logger_queue = None
generator_queue = None
archive_queue = None

exit_flag = False
threads = []

plugins = None
plugin_data = {}

####
# sig_handler
####
def sig_handler(signum, frame):
    """
    Signal Handler to manage shutdown of autosub.
    """

    global exit_flag

    print("Shutting down autosub...")

    # give the logger thread a little time write the last log message
    time.sleep(2)

    exit_flag = True

####
# check_and_init_db_table
####
def check_and_init_db_table(dbname, tablename, fields, clear_on_create = False):
    """
    Check if a table exists, if not create it with fields.
    """

    cur, con = c.connect_to_db(dbname, logger_queue, "autosub.py")

    data = {'name': tablename}
    sql_cmd = ("SELECT name FROM sqlite_master "
               "WHERE type == 'table' AND name = :name")
    cur.execute(sql_cmd, data)
    res = cur.fetchall()

    if res:
        logmsg = 'table ' + tablename + ' exists'
        c.log_a_msg(logger_queue, "autosub.py", logmsg, "DEBUG")

        if clear_on_create:
            sql_cmd = "DELETE FROM {0}".format(tablename)
            cur.execute(sql_cmd, data)
            con.commit()

            logmsg = 'cleared table ' + tablename
            c.log_a_msg(logger_queue, "autosub.py", logmsg, "DEBUG")

            con.close()

        return 0

    logmsg = 'table ' + tablename + ' does not exist'
    c.log_a_msg(logger_queue, "autosub.py", logmsg, "DEBUG")

    data = {'fields': fields}
    sql_cmd = "CREATE TABLE {0}({1})".format(tablename, fields)
    cur.execute(sql_cmd)
    con.commit()

    con.close()

    return 1

####
# init_db_statvalue()
####
def init_db_statvalue(countername, value):
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
def set_general_config_param(configitem, content):
    """
    Set a general config parameter in the database.
    """

    curc, conc = c.connect_to_db(coursedb, logger_queue, "autosub.py")

    data = {'ConfigItem' : configitem, 'Content': content}
    sql_cmd = ("INSERT OR REPLACE INTO GeneralConfig (ConfigItem, Content) "
               "VALUES(:ConfigItem, :Content)")
    curc.execute(sql_cmd, data)
    conc.commit()

    conc.close()

###
# set_plugin_data
###
def set_plugin_data(plugin_data):
    """
    Set the parameters for plugins, given in the config
    into the table PluginData
    """
    cur, con = c.connect_to_db(coursedb, logger_queue, "autosub.py")

    db_items = []

    for plugin_name, items in plugin_data.items():
        for item in items:
            parameter_name = item[0]
            value = item[1]
            db_items.append( (plugin_name, parameter_name, value) )

    sql_cmd = ("INSERT INTO PluginData (PluginName, ParameterName, Value) "
               "VALUES (?,?,?)")
    cur.executemany(sql_cmd, db_items)
    con.commit()

    logmsg = 'Set parameters for plugins'
    c.log_a_msg(logger_queue, "autosub.py", logmsg, "DEBUG")

    con.close()

####
# load_specialmessage_to_db
####
def load_specialmessage_to_db(env, msgname, filename):
    """
    Load the SpecialMessages in the db.
    """

    template = env.get_template(filename)
    data = {'course_name' : course_name, "submission_email" : smtpmail,
            'allow_requests': allow_requests}
    template = template.render(data)

    curc, conc = c.connect_to_db(coursedb, logger_queue, "autosub.py")

    data = {'EventName': msgname, 'EventText': template}
    sql_cmd = ("INSERT OR REPLACE INTO SpecialMessages (EventName, EventText) "
               "VALUES(:EventName, :EventText)")
    curc.execute(sql_cmd, data)
    conc.commit()

    conc.close()

####
# parse_config
####
def parse_config(config):
    """
    Parse config file and extact configuration for system
    """

    global imapserver, imapuser, imappasswd, imapmail, imapsecurity, imapport
    global smtpserver, smtpuser, smtppasswd, smtpmail, smtpsecurity, smtpport
    global num_workers, poll_period, semesterdb, coursedb, log_dir,\
           log_threshhold, server_timeout, mail_retries
    global course_name, course_mode, tasks_dir, specialmsgs_dir
    global auto_advance, allow_requests

    global plugins
    global plugin_data


    ####################
    #    IMAPSERVER    #
    ####################

    try:
        imapserver = config.get('imapserver', 'servername')
        imapuser = config.get('imapserver', 'username')
        imappasswd = config.get('imapserver', 'password', raw = True)
        imapmail = config.get('imapserver', 'email')
    except:
        print("Something went wrong reading your IMAP configuration.")
        print("Did you specify server, user, password and email correctly?")
        print("Exiting...")
        sys.exit(-1)

    try:
        imapsecurity = config.get('imapserver', 'security')
        if imapsecurity not in ['none', 'ssl', 'starttls']:
            print("Invalid value for IMAP security. Assuming ssl")
            imapsecurity = 'ssl'
    except:
        imapsecurity = 'ssl'

    try:
        imapport = config.getint('imapserver', 'serverport')
    except:
        if imapsecurity == 'ssl':
            imapport = 993
        else:
            imapport = 143

    ####################
    #    SMTPSERVER    #
    ####################
    try:
        smtpserver = config.get('smtpserver', 'servername')
        smtpuser = config.get('smtpserver', 'username')
        smtppasswd = config.get('smtpserver', 'password', raw = True)
        smtpmail = config.get('smtpserver', 'email')

    except:
        print("Something went wrong reading your SMTP configuration.")
        print("Did you specify server, user, password and email correctly?")
        print("Exiting...")
        sys.exit(-1)

    try:
        smtpsecurity = config.get('smtpserver', 'security')
        if smtpsecurity not in ['none', 'ssl', 'starttls']:
            print("Invalid value for SMTP security. Assuming ssl")
            smtpsecurity = 'ssl'
    except:
        smtpsecurity = 'ssl'

    try:
        smtpport = config.getint('smtpserver', 'serverport')
    except:
        if smtpsecurity == 'ssl':
            smtpport = 465
        elif smtpsecurity == 'starttls':
            smtpport = 587
        else:
            smtpport = 25

    ####################
    #      SYSTEM      #
    ####################
    try:
        num_workers = config.getint('system', 'num_workers')
    except:
        print("Something went wrong reading your num_worker.")
        print("Did you specify the number of desired workers?")
        print("Exiting...")
        sys.exit(-1)

    try:
        poll_period = config.getint('system', 'poll_period')
    except:
        poll_period = 60

    try:
        semesterdb = config.get('system', 'semesterdb')
    except:
        semesterdb = os.path.abspath('semester.db')

    try:
        coursedb = config.get('system', 'coursedb')
    except:
        coursedb = os.path.abspath('course.db')

    try:
        log_dir = str(config.get('system', 'log_dir')).rstrip('/')
    except:
        log_dir = os.path.abspath('./logs')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    try:
        log_threshhold = str(config.get('system', 'log_threshhold')).upper()

        if log_threshhold not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            log_threshhold = 'INFO'
    except:
        log_threshhold = "INFO"

    try:
        server_timeout = config.getint('system', 'server_timeout')
    except:
        server_timeout = 20

    try:
        mail_retries = config.getint('system', 'mail_retries')
    except:
        mail_retries = 5

    ####################
    #      COURSE      #
    ####################
    try:
        specialmsgs_dir = str(config.get('course', 'specialmsgs_dir')).rstrip('/')
    except:
        specialmsgs_dir = os.path.abspath("SpecialMessages")

    try:
        tasks_dir = str(config.get('course', 'tasks_dir')).rstrip('/')
    except:
        print("No tasks_dir specified.")
        print("Exiting...")
        sys.exit(-1)

    try:
        course_name = config.get('course', 'course_name')
    except:
        course_name = 'No name set'

    try:
        course_mode = config.get('course', 'mode')
    except:
        course_mode = 'normal'

    try:
        auto_advance = config.get('course', 'auto_advance')
        if auto_advance == 'yes' or auto_advance == '1':
            auto_advance = True
        else:
            auto_advance = False

    except:
        auto_advance = False

    try:
        allow_requests = config.get('course', 'allow_requests')
        if allow_requests == "yes" or allow_requests == "1" or allow_requests == "once":
            allow_requests = "once"
            auto_advance = False

        elif allow_requests == "multiple":
            allow_requests = "multiple"
            auto_advance = False

        else:
            allow_requests = "no"
    except:
        allow_requests = "no"

    ####################
    #     PLUGINS      #
    ####################
    if config.has_option('course', 'plugins'):
        value = config.get('course', 'plugins')
        if not value.strip(): #empty string as value
            plugins = []
        else:
            plugins = [x.strip() for x in config.get('course', 'plugins').split(',')]
    else:
        plugins = []

    if plugins:
        for plugin_name in plugins:
            if not config.has_section(plugin_name):
                print("Found no section for plugin {}. Skipping this plugin"\
                    .format(plugin_name))
                plugins.remove(plugin_name)
                continue

            plugin_items = config.items(plugin_name)

            plugin_data.update({plugin_name : plugin_items})

####
# generate_queues
####
def generate_queues():
    """
    Generate the queues with which the threads will communicate
    """

    global job_queue, sender_queue, generator_queue, archive_queue, logger_queue

    logger_queue = queue.Queue()
    job_queue = queue.Queue()
    sender_queue = queue.Queue()
    generator_queue = queue.Queue()
    archive_queue = queue.Queue()

####
# start_logger
####
def start_logger():
    """"
    Create and start the logging thread of autosub
    """
    global threads

    logger_t = logger.AutosubLogger("logger", logger_queue, log_dir, log_threshhold)

    # make the logger thread a daemon, this way the main will clean it up before
    # terminating!
    logger_t.daemon = True
    logger_t.start()

    threads.append(logger_t)


####
# start_threads
####
def start_threads():
    """
    Create and start all threads of the autosub system
    """

    global threads

    dbs = {"semester": semesterdb, "course": coursedb}

    ######################
    #       SENDER       #
    ######################
    queues = {"sender": sender_queue, \
              "logger": logger_queue, \
              "archive": archive_queue}

    smtp_info = {"mail": smtpmail, \
                 "server": smtpserver, \
                 "user": smtpuser, \
                 "passwd": smtppasswd, \
                 "port" :smtpport, \
                 "security": smtpsecurity, \
                 "mail_retries": mail_retries}

    course_info = {"name": course_name, "mail": imapmail, "tasks_dir": tasks_dir}

    sender_t = sender.MailSender("sender", queues, dbs, smtp_info, course_info, \
                                 allow_requests)

    # make the sender thread a daemon, this way the main will clean it up before
    # terminating!
    sender_t.daemon = True
    sender_t.start()
    threads.append(sender_t)

    ######################
    #      FETCHER       #
    ######################
    queues = {"sender": sender_queue, \
              "logger": logger_queue, \
              "archive": archive_queue, \
              "generator": generator_queue, \
              "job": job_queue}

    imap_info = {"mail": imapmail, \
                 "server": imapserver, \
                 "user": imapuser, \
                 "passwd": imappasswd, \
                 "port" :imapport, \
                 "security": imapsecurity, \
                 "timeout": server_timeout}

    fetcher_t = fetcher.MailFetcher("fetcher", queues, dbs, imap_info, \
                                    poll_period, allow_requests)

    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    fetcher_t.daemon = True
    fetcher_t.start()
    threads.append(fetcher_t)

    ######################
    #     GENERATOR      #
    ######################
    queues = {"sender": sender_queue, \
              "logger": logger_queue, \
              "generator": generator_queue}

    submission_mail = imapmail

    generator_t = generator.TaskGenerator("generator", queues, dbs, \
                                          submission_mail, \
                                          tasks_dir, course_mode, allow_requests)

    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    generator_t.daemon = True
    generator_t.start()
    threads.append(generator_t)

    ######################
    #      ACTIVATOR     #
    ######################
    queues = {"sender": sender_queue, \
              "logger": logger_queue, \
              "generator": generator_queue}

    activator_t = activator.TaskActivator("activator", queues, dbs, \
                                          auto_advance, allow_requests)

    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    activator_t.daemon = True
    activator_t.start()
    threads.append(activator_t)

    ######################
    #       WORKERS      #
    ######################
    queues = {"sender": sender_queue, \
              "logger": logger_queue, \
              "generator": generator_queue, \
              "job": job_queue}

    for thread_id in range(1, num_workers + 1):
        t_name = "Worker" + str(thread_id)
        worker_t = worker.Worker(t_name, queues, dbs, tasks_dir, allow_requests)
        worker_t.daemon = True
        worker_t.start()
        threads.append(worker_t)

    ######################
    #     DAILYSTATS    #
    ######################
    dailystats_t = dailystats.DailystatsTask("dailystats", logger_queue, \
                                             semesterdb)
    # make the fetcher thread a daemon, this way the main will clean it up before
    # terminating!
    dailystats_t.daemon = True
    dailystats_t.start()
    threads.append(dailystats_t)

    c.log_a_msg(logger_queue, "Main", "All threads started successfully", "INFO")

####
# check_init_ressources
####
def check_init_ressources(config_file):
    """
    Check the ressources of autosub if they need to be created and
    initialized: databases, directories.
    """
    #####################
    #     SEMESTERDB    #
    #####################

    ####### Users ######
    fields = ("UserId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Email TEXT, "
              "RegisteredAt DATETIME, LastDone DATETIME, CurrentTask INT")
    check_and_init_db_table(semesterdb, "Users", fields)

    ##### TaskStats ####
    fields = "TaskId INTEGER PRIMARY KEY, NrSubmissions INT, NrSuccessful INT"
    check_and_init_db_table(semesterdb, "TaskStats", fields)

    ### StatCounters ###
    fields = "CounterId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Value INT"
    ret = check_and_init_db_table(semesterdb, "StatCounters", fields)
    if ret:
        # add the stat counter entries and initialize them to 0:
        init_db_statvalue('nr_mails_fetched', 0)
        init_db_statvalue('nr_mails_sent', 0)
        init_db_statvalue('nr_questions_received', 0)
        init_db_statvalue('nr_non_registered', 0)
        init_db_statvalue('nr_status_requests', 0)

    ##### UserTasks ####
    fields = ("UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, TaskNr INT, "
              "UserId INT, TaskParameters TEXT, TaskDescription TEXT, "
              "TaskAttachments TEXT, NrSubmissions INTEGER, "
              "FirstSuccessful INTEGER")
    ret = check_and_init_db_table(semesterdb, "UserTasks", fields)

    ##### SuccessfulTasks ####
    fields = "UserId INTEGER, TaskNr INTEGER, PRIMARY KEY (UserId, TaskNr)"
    ret = check_and_init_db_table(semesterdb, "SuccessfulTasks", fields)

    #### Whitelist #####
    fields = "UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, Email TEXT UNIQUE, Name TEXT"
    ret = check_and_init_db_table(semesterdb, "Whitelist", fields)

    ####################
    #  DIRECTORY USERS #
    ####################
    c.check_dir_mkdir("users", logger_queue, "autosub.py")

    #####################
    #     COURSEDB      #
    #####################

    # TaskConfiguration #
    fields = ("TaskNr INT PRIMARY KEY, TaskStart DATETIME, "
              "TaskDeadline DATETIME, TaskName TEXT, GeneratorExecutable TEXT, "
              "Language TEXT, "
              "TestExecutable TEXT, BackendInterfaceFile TEXT, Score INT, "
              "TaskOperator TEXT, TaskActive BOOLEAN")
    ret = check_and_init_db_table(coursedb, "TaskConfiguration", fields)

    ## SpecialMessages #
    fields = "EventName TEXT PRIMARY KEY, EventText TEXT"
    check_and_init_db_table(coursedb, "SpecialMessages", fields)

    # we use the .txt files to set the SpecialMessages in the database with jinja2
    env = Environment()
    env.loader = FileSystemLoader(specialmsgs_dir)

    filename = 'welcome.txt'
    load_specialmessage_to_db(env, 'WELCOME', filename)

    filename = 'usage.txt'
    load_specialmessage_to_db(env, 'USAGE', filename)

    filename = 'question.txt'
    load_specialmessage_to_db(env, 'QUESTION', filename)

    filename = 'invalidtask.txt'
    load_specialmessage_to_db(env, 'INVALID', filename)

    filename = 'congratulations.txt'
    load_specialmessage_to_db(env, 'CONGRATS', filename)

    filename = 'registrationover.txt'
    load_specialmessage_to_db(env, 'REGOVER', filename)

    filename = 'notallowed.txt'
    load_specialmessage_to_db(env, 'NOTALLOWED', filename)

    filename = 'deletedfromwhitelist.txt'
    load_specialmessage_to_db(env, 'DeletedFromWhitelist', filename)

    filename = 'curlast.txt'
    load_specialmessage_to_db(env, 'CURLAST', filename)

    filename = 'deadtask.txt'
    load_specialmessage_to_db(env, 'DEADTASK', filename)

    filename = 'tasknotsubmittable.txt'
    load_specialmessage_to_db(env, 'TASKNOTSUBMITTABLE', filename)

    filename = 'tasknotactive.txt'
    load_specialmessage_to_db(env, 'TASKNOTACTIVE', filename)

    filename = 'nomultiplerequest.txt'
    load_specialmessage_to_db(env, 'NOMULTIPLEREQUEST', filename)

    ### PluginData ###
    table_name = "PluginData"
    fields = ("PluginName TEXT, ParameterName, Value TEXT, "
              "PRIMARY KEY (PluginName,ParameterName)")
    clear_on_create = True
    ret = check_and_init_db_table(coursedb, table_name, fields, clear_on_create)
    if plugins:
        set_plugin_data(plugin_data)

    ### GeneralConfig ##
    fields = "ConfigItem Text PRIMARY KEY, Content TEXT"
    ret = check_and_init_db_table(coursedb, "GeneralConfig", fields)

    if ret:
        # default values for first time, these values can be changed during
        # operation
        set_general_config_param('registration_deadline', 'NULL')
        set_general_config_param('archive_dir', 'archive')
        set_general_config_param('admin_email', '')

    # values that are read/calculated and replaced at every new start of autosub
    set_general_config_param('course_mode', course_mode)
    set_general_config_param('course_name', course_name)
    set_general_config_param('submission_email', imapmail)
    set_general_config_param('tasks_dir', tasks_dir)
    set_general_config_param('log_dir', log_dir)
    set_general_config_param('auto_advance', auto_advance)
    set_general_config_param('allow_requests', allow_requests)

    this_script_path = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(this_script_path,config_file)
    set_general_config_param('current_config', config_file_path)

    users_dir = os.path.join(this_script_path,"users")
    set_general_config_param('users_dir', users_dir)

    # configure, which plugins are active
    if plugins:
        set_general_config_param('plugins', ','.join(plugins))
    else:
        set_general_config_param('plugins', '')

##########################
#         MAIN           #
##########################
if __name__ == '__main__':
    # end this programm with SIGUSR1
    signal.signal(signal.SIGUSR1, sig_handler)

    # Parser for options to this program
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config-file", dest="configfile", type="string", \
                      help=("Config file used for the instance of autosub."))

    parser.set_defaults(configfile="default.cfg")
    opts, args = parser.parse_args()

    # Parser for the given config file
    config = configparser.ConfigParser()

    try:
        config.readfp(open(opts.configfile))
    except:
        print("Error reading your configfile\ndaemon exited...")
        sys.exit(-1)

    parse_config(config)
    generate_queues()
    start_logger()
    check_init_ressources(opts.configfile)
    start_threads()

    logmsg = "System startup successfull using configfile '" \
             +  opts.configfile + "'"
    c.log_a_msg(logger_queue, "autosub.py", logmsg, "INFO")

    while not exit_flag:
        time.sleep(100)

    sys.exit(0)
