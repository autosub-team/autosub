########################################################################
# worker.py -- runs the actual tests of task results
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import datetime
from subprocess import Popen, PIPE
import os

import json

import common as c

class Worker(threading.Thread):
    """
    Thread that tests given user submissions.
    """

    ####
    # __init__
    ####
    def __init__(self, name, queues, dbs, tasks_dir, allow_requests):
        """
        Constructor of the Worker thread.
        """

        threading.Thread.__init__(self)
        self.name = name
        self.queues = queues
        self.dbs = dbs
        self.tasks_dir = tasks_dir
        self.allow_requests = allow_requests

    ####
    # get_task_parameters
    ####
    def get_task_parameters(self, user_id, task_nr):
        """
        Look up the taskParmeters, that were generated from the generator for
        a indididual task.
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)
        data = {'task_nr': task_nr, 'user_id': user_id}
        sql_cmd = ("SELECT TaskParameters FROM UserTasks "
                   "WHERE TaskNr == :task_nr AND UserId == :user_id")
        curs.execute(sql_cmd, data)
        params = curs.fetchone()[0]
        cons.close()
        return params

    ####
    # get_plugins
    ####
    def get_configured_plugins(self, task_nr):
        """
        Get the configured plugins for a task
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'task_nr': task_nr} #TODO: FUTURE

        sql_cmd = ("SELECT Content FROM GeneralConfig "
                   "WHERE ConfigItem == 'plugins'")
        curc.execute(sql_cmd)
        plugins = curc.fetchone()[0]
        if plugins:
            plugins_list = plugins.split(",")
        else:
            plugins_list = None
        conc.close()

        return plugins_list

    ####
    # get_configured_backend_interface
    ####
    def get_configured_backend_interface(self, task_nr):
        """
        Get the configured common file configured for the task
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'task_nr': task_nr}
        sql_cmd = ("SELECT BackendInterfaceFile FROM TaskConfiguration "
                   "WHERE TaskNr == :task_nr")
        curc.execute(sql_cmd, data)
        common_file = curc.fetchone()[0]
        conc.close()

        return common_file

    ####
    # get_scriptpath
    ####
    def get_scriptpath(self, task_nr):
        """
        Get the path to the tester script for task task_nr.
        Returns None if not proper config.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'task_nr': task_nr}
        sql_cmd = ("SELECT TaskName, TestExecutable FROM TaskConfiguration "
                   "WHERE TaskNr == :task_nr")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()

        if not res:
            logmsg = ("Failed to fetch Configuration for TaskNr: {0} from the "
                      "database! Table TaskConfiguration corrupted?").format(task_nr)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

            scriptpath = None
        else:
            task_name = res[0]
            tester_name = res[1]

            scriptpath = self.tasks_dir + "/" + task_name + "/" + tester_name

        conc.close()
        return scriptpath

    ####
    # get_task_dir
    ####
    def get_task_dir(self, task_nr):
        """
        Get the path to taskfolder of task_nr.
        Returns None if not proper config.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'task_nr': task_nr}
        sql_cmd = ("SELECT TaskName FROM TaskConfiguration "
                   "WHERE TaskNr == :task_nr")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()

        if not res:
            logmsg = ("Failed to fetch Configuration for TaskNr: {0} from the "
                      "database! Table TaskConfiguration corrupted?").format(task_nr)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return None

        else:
            task_name = res[0]

        sql_cmd = ("SELECT Content FROM GeneralConfig "
                   "WHERE ConfigItem == 'tasks_dir'")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()

        tasks_dir = res[0]
        #TODO: Error check

        task_dir = os.path.join(tasks_dir, task_name)

        return task_dir

    ####
    # handle_test_result
    ####
    def handle_test_result(self, test_res, user_id, user_email, task_nr, message_id):
        """
        Act based on the result of the test
        """
        SUCCESS = 0
        FAILURE = 1
        SECURITYALERT = 2
        TASKERROR= 3

        if test_res == FAILURE: # not 0 returned
        #####################
        #       FAILED      #
        #####################
            logmsg = "Test failed! User: {0} Task: {1}".format(user_id, \
                                                               task_nr)
            logmsg = logmsg + " return value:" + str(test_res)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

            c.send_email(self.queues["sender"], user_email, user_id, \
                        "Failed", task_nr, "", message_id)

        elif test_res == SECURITYALERT:
        #####################
        #   SECURITY ALERT  #
        #####################
            logmsg = "SecAlert: This test failed due to probable attack by user!"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

            c.send_email(self.queues["sender"], "", user_id, \
                         "SecAlert", task_nr, "", message_id)

        elif test_res == TASKERROR:
        #####################
        #     TASK ERROR    #
        #####################
            logmsg = ("TaskAlert: This test for TaskNr {0} and User {1} failed "
                      " due an error with task/testbench analyzation!").format(task_nr, user_id)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

            # alert to admins
            c.send_email(self.queues["sender"], "", user_id, \
                         "TaskAlert", task_nr, "", message_id)

            # error notice to user
            c.send_email(self.queues["sender"], user_email, user_id, \
                         "TaskErrorNotice", task_nr, "", message_id)

        elif test_res == SUCCESS: # 0 returned
        #####################
        #       SUCCESS     #
        #####################
            logmsg = "Test succeeded! User: {0} Task: {1}".format(user_id, task_nr)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

            plugins = self.get_configured_plugins(task_nr)

            if not plugins:
                # Notify, the user that the submission was successful
                c.send_email(self.queues["sender"], user_email, user_id, \
                         "Success", task_nr, "", message_id)
            else:
                self.execute_plugins(user_id,task_nr, plugins)

                c.send_email(self.queues["sender"], user_email, user_id, \
                         "PluginResult", task_nr, "", message_id)


            # no initiate creation of next task if allow_requests set
            if self.allow_requests != "no":
                return

            # initiate generation of next higher task_nr task for user (if possible)
            next_task_nr = int(task_nr) + 1
            self.initiate_next_task(user_id, user_email, int(task_nr), next_task_nr)

    ####
    # create_error_plugin_msg
    ####
    def create_error_plugin_msg(self, user_task_dir, user_id, task_nr):
        json_data = {
            "Subject" : "Plugin Error Task{}".format(task_nr),
            "Message" : ("There is no feedback from the plugin. "
                         "Please contact the course admin"),
            "IsSuccess" : False \
        }

        file_name = os.path.join(user_task_dir, "plugin_msg.json")

        with open(file_name, "w") as f:
            json.dump(json_data, f)

    ####
    # execute_plugins
    ####
    def execute_plugins(self, user_id, task_nr, plugins):
        user_task_dir = "users/{0}/Task{1}".format(user_id, task_nr)
        task_dir = self.get_task_dir(task_nr)

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        for plugin_name in plugins:
            # check if plugin script exists
            plugin_script="plugins/"+plugin_name + ".py"
            if not os.path.isfile(plugin_script):
                logmsg = "Plugin script for plugin {} does not exist".format(plugin_name)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                self.create_error_plugin_msg(user_task_dir, user_id, task_nr)
                return

            # get configutation
            plugin_prefix = plugin_name + "_"
            sql_cmd = ("SELECT ConfigItem, Content FROM GeneralConfig "
                       " WHERE ConfigItem LIKE :plugin_prefix")
            data = {"plugin_prefix" : plugin_prefix + "%"}

            curc.execute(sql_cmd, data)
            rows = curc.fetchall()
            plugin_params = {"user_task_dir": user_task_dir,
                             "task_dir" : task_dir,
                             "user_id": user_id,
                             "task_nr": task_nr}

            for row in rows:
                key = row["ConfigItem"].replace(plugin_prefix,"")
                value = row["Content"]

                plugin_params.update({key:value})

            plugin_command = []
            plugin_command.append("python3")
            plugin_command.append(plugin_script)

            for key, value in plugin_params.items():
                plugin_command.append("--" + key)
                plugin_command.append(value)

            # run the plugin script and log the stderr and stdout
            logmsg = "Running plugin script with arguments:{0}"\
                .format(plugin_command)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            # Popen in asynch, but communicate waits
            process = Popen(plugin_command, stdout=PIPE, stderr=PIPE)
            plugin_msg, plugin_error = process.communicate()
            plugin_msg = plugin_msg.decode('UTF-8')
            plugin_error = plugin_error.decode('UTF-8')
            plugin_res = process.returncode
            log_src = "Plugin-{}{}({})".format(plugin_name,str(task_nr),str(user_id))

            if plugin_msg:
                c.log_task_msg(self.queues["logger"], log_src, plugin_msg, "INFO")
            if plugin_error:
                c.log_task_error(self.queues["logger"], log_src, plugin_error, "ERROR")

            logmsg = "Plugin returned with " + str(plugin_res)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
            if plugin_res: #not 0
                self.create_error_plugin_msg(user_task_dir, user_id, task_nr)

    ####
    # initiate_next_task
    ####
    def initiate_next_task(self, user_id, user_email, current_task_nr, next_task_nr):
        """
        Initiate the generation of the next task for the user if he has not got
        the task already and if it has already started
        """


        if not c.is_valid_task_nr(self.dbs["course"], next_task_nr, \
                                  self.queues["logger"], self.name):
            return

        if current_task_nr < next_task_nr:
        # user did not get this task yet
            task_start = c.get_task_starttime(self.dbs["course"], \
                                              next_task_nr, \
                                              self.queues["logger"], \
                                              self.name)

            if task_start <= datetime.datetime.now():
                # task has already started
                c.generate_task(self.queues["generator"], user_id, next_task_nr, user_email, "")

            else:
                c.send_email(self.queues["sender"], str(user_email), \
                             str(user_id), "CurLast", \
                             str(next_task_nr), "", "")

    ####
    # handle_job
    ####
    def handle_job(self, nextjob):
        """
        Run the test script for the given submission and act on the test result
        """

        task_nr = str(nextjob.get('task_nr'))
        user_id = str(nextjob.get('user_id'))
        user_email = str(nextjob.get('user_email'))
        message_id = str(nextjob.get('message_id'))

        logmsg = "{0} got a new job: {1} from the user with id {2}".format(self.name, task_nr, \
                                                                           user_id)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

        # get the task parameters
        task_params = self.get_task_parameters(user_id, task_nr)

        # get the path to the test script
        scriptpath = self.get_scriptpath(task_nr)

        # get the configured common file
        configured_backend_interface = self.get_configured_backend_interface(task_nr)

        if not scriptpath:
            logmsg = "Could not fetch test script from database"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return

        if not os.path.isfile(scriptpath):
            logmsg = "Test script does not exist"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return

        # run the test script and log the stderr and stdout
        command = [scriptpath, user_id, task_nr, task_params, configured_backend_interface]
        logmsg = "Running test script with arguments: {0}".format(command)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        # Popen in asynch, but communicate waits
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        test_msg, test_error = process.communicate()
        test_msg = test_msg.decode('UTF-8')
        test_error = test_error.decode('UTF-8')
        test_res = process.returncode
        log_src = "Tester{0}({1})".format(str(task_nr), user_id)

        if test_msg:
            c.log_task_msg(self.queues["logger"], log_src, test_msg, "INFO")
        if test_error:
            c.log_task_error(self.queues["logger"], log_src, test_error, "ERROR")

        # act based on the result
        self.handle_test_result(test_res, user_id, user_email, task_nr, message_id)

    ####
    # run
    ####
    def run(self):
        """
        Thread code for the worker thread.
        """

        logmsg = "Starting " + self.name
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

        while True:
            logmsg = self.name + ": waiting for a new job."
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

            # blocking wait on job queue
            nextjob = self.queues["job"].get(True)

            self.handle_job(nextjob)
