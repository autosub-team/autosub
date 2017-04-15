########################################################################
# generator.py -- Generates the individual tasks when needed
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
from subprocess import Popen, PIPE

import common as c

class taskGenerator(threading.Thread):
    """
     Thread to generate unique tasks using a task generator scripts.
    """

    ####
    # init
    ####
    def __init__(self, thread_id, name, gen_queue, sender_queue, logger_queue, coursedb, \
                     semesterdb, submission_email):
        """
        Constructor for the thread.
        """

        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.gen_queue = gen_queue
        self.sender_queue = sender_queue
        self.logger_queue = logger_queue
        self.coursedb = coursedb
        self.semesterdb = semesterdb
        self.submission_email = submission_email

    ####
    # get_challenge_mode
    ###
    def get_challenge_mode(self):
        """
        Get the configured challenge mode
        """

        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)

        sql_cmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem = 'challenge_mode'"
        curc.execute(sql_cmd)
        challenge_mode = curc.fetchone()

        conc.close()

        return str(challenge_mode[0])

    ####
    # generator_loop
    ####
    def generator_loop(self):
        """
        Loop code for the generator thread
        """

        #blocking wait on gen_queue
        next_gen_msg = self.gen_queue.get(True)
        logmsg = "gen_queue content:" + str(next_gen_msg)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        task_nr = next_gen_msg.get('task_nr')
        user_id = next_gen_msg.get('user_id')
        user_email = next_gen_msg.get('user_email')
        messageid = next_gen_msg.get('messageid')

        #generate the directory for the task
        task_dir = 'users/' + str(user_id) + "/Task"+str(task_nr)
        c.check_dir_mkdir(task_dir, self.logger_queue, self.name)

        #generate the task description
        desc_dir = task_dir + "/desc"
        c.check_dir_mkdir(desc_dir, self.logger_queue, self.name)

        # check if there is a generator executable configured in the database
        # if not fall back on static generator script.
        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)

        data = {'TaskNr': task_nr}
        sql_cmd = ("SELECT GeneratorExecutable FROM TaskConfiguration "
                   "WHERE TaskNr== :TaskNr")
        curc.execute(sql_cmd, data)
        generatorname = curc.fetchone()

        if generatorname != None:
            data = {'TaskNr': task_nr}
            sql_cmd = "SELECT PathToTask FROM TaskConfiguration WHERE TaskNr == :TaskNr"
            curc.execute(sql_cmd, data)
            path = curc.fetchone()
            scriptpath = str(path[0]) + "/" + str(generatorname[0])
        else:
            scriptpath = "tasks/task" + str(task_nr) + "/./generator.sh"

        challenge_mode = self.get_challenge_mode()

        command = [scriptpath, str(user_id), str(task_nr), self.submission_email,\
                   str(challenge_mode), self.semesterdb]

        logmsg = "generator command with arguments: {0} ".format(command)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        process = Popen(command, stdout=PIPE, stderr=PIPE)
        generator_msg, generator_error = process.communicate()
        generator_msg = generator_msg.decode('UTF-8')
        generator_error = generator_error.decode('UTF-8')
        generator_res = process.returncode
        log_src = "Generator{0}({1})".format(str(task_nr), str(user_id))

        if generator_msg:
            c.log_task_msg(self.logger_queue, log_src, generator_msg, "INFO")
        if generator_error:
            c.log_task_error(self.logger_queue, log_src, generator_error, "ERROR")

        if generator_res: # not 0 returned
            logmsg = "Failed to call generator script, return value: " + \
                     str(generator_res)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        logmsg = "Generated individual task for user/tasknr:" + str(user_id) + "/" + \
                 str(task_nr)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        c.send_email(self.sender_queue, str(user_email), str(user_id), \
                     "Task", str(task_nr), "Your personal example", str(messageid))

        conc.close()

    ####
    # run
    ####
    def run(self):
        """
        Thread code for the generator thread.
        """

        c.log_a_msg(self.logger_queue, self.name, "Task Generator thread started", "INFO")

        while True:
            self.generator_loop()
