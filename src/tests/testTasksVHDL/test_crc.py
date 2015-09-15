#!/usr/bin/env python3
import taskTestBase
import os
import unittest

class test_crc(taskTestBase.taskTestBase):

    def test_crc_descFilesCreation(self):     
        expected_files=[]
        expected_files.append('solution_{0}_Task{1}.txt'.format(self.userId,self.taskNr))
        expected_files.append('desc_{0}_Task{1}.pdf'.format(self.userId,self.taskNr))
        expected_files.append('fsr_beh.vhdl')
        expected_files.append('fsr.vhdl')
        expected_files.append('crc_beh.vhdl')
        expected_files.append('crc.vhdl') 
        expected_files.append('crc_tb_exam.vhdl')

        self.checkDescFiles("crc",expected_files)

    def test_crc_descVHDLFilesAnalyze(self):
        files= ["fsr.vhdl","crc.vhdl","fsr_beh.vhdl","crc_beh.vhdl"]
        self.checkDescVHDLFiles("crc",files)


if __name__ == '__main__':
    unittest.main()
