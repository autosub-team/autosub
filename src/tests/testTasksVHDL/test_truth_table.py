#!/usr/bin/env python3
import taskTestBase
import os
import unittest

class test_truth_table(taskTestBase.taskTestBase):

    def test_truth_table_descFilesCreation(self):       
        expected_files=[]
        expected_files.append('solution_{0}_Task{1}.txt'.format(self.userId,self.taskNr))
        expected_files.append('desc_{0}_Task{1}.pdf'.format(self.userId,self.taskNr))
        expected_files.append('truth_table_beh.vhdl')
        expected_files.append('truth_table.vhdl') 
        expected_files.append('truth_table_tb_exam.vhdl')

        self.checkDescFiles("truth_table",expected_files)

    def test_truth_table_descVHDLFilesAnalyze(self):
        files= ["truth_table.vhdl","truth_table_beh.vhdl"]
        self.checkDescVHDLFiles("truth_table",files)

    def test_truth_table_testerExecution(self):
        self.checkTester("truth_table","32759")

if __name__ == '__main__':
    unittest.main()
