#!/usr/bin/env python3
import taskTestBase
import os
import unittest

class test_gates(taskTestBase.taskTestBase):

    def test_gates_descFilesCreation(self):
        expected_files=[]
        expected_files.append('solution_{0}_Task{1}.txt'.format(self.userId,self.taskNr))
        expected_files.append('desc_{0}_Task{1}.pdf'.format(self.userId,self.taskNr))
        expected_files.append('gates_beh.vhdl')
        expected_files.append('gates.vhdl')  
        expected_files.append('IEEE_1164_Gates_pkg.vhdl')
        expected_files.append('IEEE_1164_Gates.vhdl')
        expected_files.append('IEEE_1164_Gates_beh.vhdl')
        expected_files.append('gates_tb_exam.vhdl')

        self.checkDescFiles("gates",expected_files)

    def test_gates_descVHDLFilesAnalyze(self):
        files= ["IEEE_1164_Gates_pkg.vhdl","IEEE_1164_Gates.vhdl","IEEE_1164_Gates_beh.vhdl","gates.vhdl","gates_beh.vhdl"]
        self.checkDescVHDLFiles("gates",files)


if __name__ == '__main__':
    unittest.main()
