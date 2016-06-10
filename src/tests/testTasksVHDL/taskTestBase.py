#!/usr/bin/env python3
import unittest
import os
import shutil
import random
import subprocess
import sqlite3 as lite

used_tool_prefix = "ghdl_" #ISE_

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

class taskTestBase(unittest.TestCase):

    def run_generator(self, task_name):
        gen_command = ("tasks/implementation/VHDL/{0}/"
                       "generator.sh").format(task_name)
        tmpself = [gen_command, str(self.userId), str(self.taskNr), \
                   str(self.mode), str(self.semesterdb)]
        #pipe away add_to_usertask error messages that appear if no db exists
        ret = subprocess.check_call(tmpself, stdout=subprocess.PIPE, \
                                    stderr=subprocess.PIPE)
        self.assertEqual(ret, 0, \
                         "Error with generator.sh for task " + task_name)

    def runTester(self, task_name, taskParameters):
        executable = "tasks/implementation/VHDL/{0}/{1}tester.sh".format(task_name,used_tool_prefix)
        tmpself = [executable, str(self.userId), \
                   str(self.taskNr), str(taskParameters)]
        ret = subprocess.check_call(tmpself, stdout=subprocess.PIPE, \
                                    stderr=subprocess.PIPE)  #pipe away output
        self.assertEqual(ret, 0, "Error with tester.sh for task " + task_name)

    def checkDescFiles(self, task_name, expected_files):
        self.run_generator(task_name)

        files = os.listdir("users/{0}/Task{1}/desc".format(self.userId, \
                                                           self.taskNr))

        files.sort()
        expected_files.sort()

        self.assertEqual(files, expected_files, \
                         "Not all expected files generated for task " + \
                         task_name)

    def checkWithGHDL(self, files):
        for f in files:
            ret = subprocess.check_call(["ghdl", "-a", f])
            self.assertEqual(ret, 0, "GHDL error at: ghdl " + f)

    def checkDescVHDLFiles(self, task_name, files):
        self.run_generator(task_name)

        savedPath = os.getcwd()

        os.chdir("users/{0}/Task{1}/desc".format(self.userId, self.taskNr))

        self.checkWithGHDL(files)

        os.chdir(savedPath)

    def checkTester(self, task_name, taskParameters):
        src = "tests/testTasksVHDL/testsubmissions/{0}".format(task_name)
        dst = "users/{0}/Task{1}".format(self.userId, self.taskNr)
        copytree(src, dst)

        self.runTester(task_name, taskParameters)

    def clean_usertasks(self):
        con = lite.connect(self.semesterdb)
        cur = con.cursor()

        #drop if exists
        try:
            sqlcmd = "DROP TABLE UserTasks;"
            cur.execute(sqlcmd)
            con.commit()
        except:
            pass

        sqlcmd = ("CREATE TABLE UserTasks "
                  "(UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, TaskNr INT, "
                  "UserId INT, TaskParameters TEXT, TaskDescription TEXT, "
                  "TaskAttachments TEXT, NrSubmissions INTEGER, "
                  "FirstSuccessful INTEGER);")
        cur.execute(sqlcmd)
        con.commit()
        con.close()

    def clean_usersdir(self):
        if os.path.exists("users"):
            shutil.rmtree("users")
        os.mkdir("users")

    def new_userdir(self):
        self.taskNr = random.randrange(1, 7)
        self.userId = random.randrange(1, 200)
        os.mkdir("users/{0}".format(self.userId))
        os.mkdir("users/{0}/Task{1}".format(self.userId, self.taskNr))

    def setUp(self):
        self.semesterdb = "/tmp/semester.db"
        self.mode = "normal"
        self.clean_usertasks()
        self.clean_usersdir()
        self.new_userdir()

    def tearDown(self):
        pass
