#!/usr/bin/env python3
import taskTestBase
import os
import unittest

class test_pwm(taskTestBase.taskTestBase):

    def test_pwm_descFilesCreation(self):
        expected_files=[]
        expected_files.append('solution_{0}_Task{1}.txt'.format(self.userId,self.taskNr))
        expected_files.append('desc_{0}_Task{1}.pdf'.format(self.userId,self.taskNr))
        expected_files.append('pwm.vhdl')
        expected_files.append('pwm_beh.vhdl') 
        expected_files.append('pwm_tb_exam.vhdl')

        self.checkDescFiles("pwm",expected_files)

    def test_pwm_descVHDLFilesAnalyze(self):
        files= ["pwm.vhdl","pwm_beh.vhdl"]
        self.checkDescVHDLFiles("pwm",files)

    def test_pwm_testerExecution(self):
        self.checkTester("pwm","655361400")

if __name__ == '__main__':
    unittest.main()
