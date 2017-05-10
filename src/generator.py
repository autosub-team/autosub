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

class TaskGenerator(threading.Thread):
    """
     Thread to generate unique tasks using task generator scripts.
    """

    ####
    # init
    ####
    def __init__(self, name, queues, dbs, submission_mail, tasks_dir, \
                 course_mode):
        """
        Constructor for the thread.
        """

        threading.Thread.__init__(self)
        self.name = name

        self.queues = queues
        self.dbs = dbs
        self.submission_mail = submission_mail
        self.tasks_dir = tasks_dir
        self.course_mode = course_mode

    ####
    # get_scriptpath
    ####
    def get_scriptpath(self, task_nr):
        """
        Get the path to the generator script for task task_nr.
        Returns None if not proper config.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'task_nr': task_nr}
        sql_cmd = ("SELECT TaskName, GeneratorExecutable FROM TaskConfiguration "
                   "WHERE TaskNr == :task_nr")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()

        if not res:
            logmsg = ("Failed to fetch Configuration for TaskNr {0} from the "
                      "database! Table TaskConfiguration corrupted?").format(task_nr)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

            scriptpath = None
        else:
            task_name = res[0]
            generator_name = res[1]

            scriptpath = self.tasks_dir + "/" + task_name + "/" + generator_name

        conc.close()
        return scriptpath

    ####
    # generator_loop
    ####
    def generator_loop(self):
        """
        Loop code for the generator thread
        """

        # blocking wait on gen_queue
        next_gen_msg = self.queues["generator"].get(True)
        logmsg = "gen_queue content:" + str(next_gen_msg)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        task_nr = next_gen_msg.get('task_nr')
        user_id = next_gen_msg.get('user_id')
        user_email = next_gen_msg.get('user_email')
        message_id = next_gen_msg.get('messageid')

        # generate the directory for the task in the space of the user
        usertask_dir = 'users/' + str(user_id) + "/Task"+str(task_nr)
        c.check_dir_mkdir(usertask_dir, self.queues["logger"], self.name)

        # generate the folder for the task description
        desc_dir = usertask_dir + "/desc"
        c.check_dir_mkdir(desc_dir, self.queues["logger"], self.name)

        # get the path to the generator script
        scriptpath = self.get_scriptpath(task_nr)

        if not scriptpath:
            return

        #TODO: Check if script exists?

        command = [scriptpath, str(user_id), str(task_nr), self.submission_mail,\
                   str(self.course_mode), self.dbs["semester"]]

        logmsg = "generator command with arguments: {0} ".format(command)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        process = Popen(command, stdout=PIPE, stderr=PIPE)
        generator_msg, generator_error = process.communicate()
        generator_msg = generator_msg.decode('UTF-8')
        generator_error = generator_error.decode('UTF-8')
        generator_res = process.returncode
        log_src = "Generator{0}({1})".format(str(task_nr), str(user_id))

        if generator_msg:
            c.log_task_msg(self.queues["logger"], log_src, generator_msg, "INFO")
        if generator_error:
            c.log_task_error(self.queues["logger"], log_src, generator_error, "ERROR")

        if generator_res: # not 0 returned
            logmsg = "Failed executing the generator script, return value: " + \
                     str(generator_res)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        logmsg = "Generated individual task for user/tasknr:" + str(user_id) + "/" + \
                 str(task_nr)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        c.send_email(self.queues["sender"], str(user_email), str(user_id), \
                     "Task", str(task_nr), "Your personal example", str(message_id))

    ####
    # run
    ####
    def run(self):
        """
        Thread code for the generator thread.
        """

        c.log_a_msg(self.queues["logger"], self.name, "Task Generator thread started", "INFO")

        while True:
            self.generator_loop()
