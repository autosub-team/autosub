#!/usr/bin/env python3
import taskTestBase
import os
import unittest

class test_arithmetic(taskTestBase.taskTestBase):

    def test_arithmetic_descFilesCreation(self):
        expected_files=[]
        expected_files.append('solution_{0}_Task{1}.txt'.format(self.userId,self.taskNr))
        expected_files.append('desc_{0}_Task{1}.pdf'.format(self.userId,self.taskNr))
        expected_files.append('arithmetic_beh.vhdl')
        expected_files.append('arithmetic.vhdl') 
        expected_files.append('arithmetic_tb_exam.vhdl')

        self.checkDescFiles("arithmetic",expected_files)

    def test_arithmetic_descVHDLFilesAnalyze(self):
        files= ["arithmetic.vhdl","arithmetic_beh.vhdl"]
        self.checkDescVHDLFiles("arithmetic",files)

    def test_arithmetic_testerExecution(self):
        self.checkTester("arithmetic","146607")       
        
if __name__ == '__main__':
    unittest.main()
