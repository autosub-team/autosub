#!/usr/bin/env python3
import unittest
import os
import shutil
import random
import mock
import string
import subprocess

class taskTestBase (unittest.TestCase):

    def run_generator(self,task_name):
        ret=subprocess.check_call(["tasks/implementation/VHDL/{0}/generator.sh".format(task_name),str(self.userId),str(self.taskNr)],stdout=subprocess.PIPE,stderr=subprocess.PIPE )  #pipe away the add_to_usertast error messages that appear if no db exists
        self.assertEqual(ret,0,"Error with generator.sh for task "+task_name)

    def checkDescFiles(self,task_name,expected_files):
        self.run_generator(task_name)

        files=os.listdir("users/{0}/Task{1}/desc".format(self.userId,self.taskNr))

        files.sort()
        expected_files.sort()

        self.assertEqual(files,expected_files,"Not all expected files generated for task "+task_name)  

    def checkWithGHDL(self,files):
        for f in files:
            ret=subprocess.check_call(["ghdl","-a",f])
            self.assertEqual(ret,0,"GHDL error at: ghdl "+f)  

    def checkDescVHDLFiles(self,task_name,files):
        self.run_generator(task_name)

        savedPath = os.getcwd()

        os.chdir("users/{0}/Task{1}/desc".format(self.userId,self.taskNr))
                
        self.checkWithGHDL(files)

        os.chdir(savedPath)
         

    def setUp(self):
        if not os.path.exists("users"):
            os.mkdir("users")

        self.taskNr=random.randrange(1,7)
        self.userId=random.randrange(1,200)

        os.mkdir("users/{0}".format(self.userId))
        os.mkdir("users/{0}/Task{1}".format(self.userId,self.taskNr))

    def tearDown(self):
        shutil.rmtree("users/{0}".format(self.userId))
