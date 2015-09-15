#!/usr/bin/env python3
import taskTestBase
import os
import unittest

class test_fsm(taskTestBase.taskTestBase):

    def test_fsm_descFilesCreation(self):     
        expected_files=[]
        expected_files.append('solution_{0}_Task{1}.txt'.format(self.userId,self.taskNr))
        expected_files.append('desc_{0}_Task{1}.pdf'.format(self.userId,self.taskNr))
        expected_files.append('fsm_pkg.vhdl')
        expected_files.append('fsm.vhdl')
        expected_files.append('fsm_beh.vhdl') 
        expected_files.append('fsm_tb_exam.vhdl')

        self.checkDescFiles("fsm",expected_files)

    def test_fsm_descVHDLFilesAnalyze(self):
        files= ["fsm_pkg.vhdl","fsm.vhdl","fsm_beh.vhdl"]
        self.checkDescVHDLFiles("fsm",files)


if __name__ == '__main__':
    unittest.main()
