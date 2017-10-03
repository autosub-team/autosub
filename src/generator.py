########################################################################
# generator.py -- Generates the individual tasks when needed
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
from subprocess import Popen, PIPE
import os
import shutil

import common as c

class TaskGenerator(threading.Thread):
    """
     Thread to generate unique tasks using task generator scripts.
    """

    ####
    # init
    ####
    def __init__(self, name, queues, dbs, submission_mail, tasks_dir, \
                 course_mode, allow_requests):
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
        self.allow_requests = allow_requests

    ####
    # get_scriptinfo
    ####
    def get_scriptinfo(self, task_nr):
        """
        Get the path to the generator script and chosen language for task task_nr.
        Returns None if not proper config.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'task_nr': task_nr}
        sql_cmd = ("SELECT TaskName, GeneratorExecutable, Language FROM TaskConfiguration "
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
            language = res[2]

            scriptpath = self.tasks_dir + "/" + task_name + "/" + generator_name

        conc.close()
        return (scriptpath, language)

    ####
    # delete_usertask
    ####
    def delete_usertask(self, user_id, task_nr):
        """
        Delete existing usertask and its structures
        """

        # delete db entry
        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)
        data = {"user_id": user_id,
                "task_nr": task_nr}
        sql_cmd = ("DELETE FROM UserTasks "
                   "WHERE TaskNr == :task_nr AND UserId == :user_id")

        # remove directory
        usertask_dir = 'users/' + str(user_id) + "/Task"+str(task_nr)
        shutil.rmtree(usertask_dir)

        curs.execute(sql_cmd, data)
        cons.commit()
        cons.close()

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
        message_id = next_gen_msg.get('message_id')

        # requested task is a valid task?
        if not c.is_valid_task_nr(self.dbs["course"], task_nr, \
                                  self.queues["logger"], self.name):
            logmsg = ("Generator was given the task to create non valid TaskNr {0}. "
                      "This should not happen!").format(task_nr)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return

        # check if user already got this task
        already_received = c.user_received_task(self.dbs["semester"], user_id, \
                                                task_nr, self.queues["logger"], \
                                                self.name)

        if already_received:
            if self.allow_requests == "multiple":
                logmsg = ("User with Id {0} TaskNr {1} already got this task, "
                          "deleting it to make place for new").format(user_id, task_nr)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")
                self.delete_usertask(user_id, task_nr)
            else:
                logmsg = ("User with Id {0} TaskNr {1} already got this task, "
                          "multiple request not allowed for this course").format(user_id, task_nr)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

                c.send_email(self.queues["sender"], str(user_email), str(user_id), \
                             "NoMultipleRequest", str(task_nr), "", str(message_id))
                return

        # generate the directory for the task in the space of the user
        usertask_dir = 'users/' + str(user_id) + "/Task"+str(task_nr)
        c.check_dir_mkdir(usertask_dir, self.queues["logger"], self.name)

        # generate the folder for the task description
        desc_dir = usertask_dir + "/desc"
        c.check_dir_mkdir(desc_dir, self.queues["logger"], self.name)

        # get the path to the generator script
        scriptpath, language = self.get_scriptinfo(task_nr)

        # check the path
        if not scriptpath or not os.path.isfile(scriptpath):
            logmsg = "Could not find generator script for task{0}".format(task_nr)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return

        command = [scriptpath, str(user_id), str(task_nr), self.submission_mail,\
                   str(self.course_mode), self.dbs["semester"], str(language)]

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
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return

        logmsg = "Generated individual task for user/task_nr:" + str(user_id) \
                 + "/" + str(task_nr)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

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
