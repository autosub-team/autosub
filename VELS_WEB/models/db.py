# -*- coding: utf-8 -*-

###################################################
################### SEMESTER ######################
###################################################
semester= DAL('sqlite://semester.db')

semester.define_table('Users',
    Field('UserId','integer'),
    Field('Name','string'),
    Field('Email','string'),
    Field('RegisteredAt','datetime'),
    Field('LastDone','datetime'),
    Field('CurrentTask','integer'),
    migrate=False,primarykey=['UserId'])
Users= semester.Users

semester.define_table('TaskStats',
    Field('TaskId', 'integer', unique=True),
    Field('NrSubmissions', 'integer'),
    Field('NrSuccessful', 'integer'),
    migrate=False, primarykey=['TaskId'])
TaskStats= semester.TaskStats

semester.define_table('StatCounters',
    Field('CounterId', 'integer', unique=True),
    Field('Name','string'),
    Field('Value','integer'),
    migrate=False, primarykey=['CounterId'])
StatCounters= semester.StatCounters

semester.define_table('UserTasks',
    Field('UniqueId', 'integer',unique=True),
    Field('TaskNr', 'integer'),
    Field('UserId', 'integer'),
    Field('TaskParameters', 'string'),
    Field('TaskDescription', 'string'),
    Field('TaskAttachments', 'string'),
    Field('NrSubmissions', 'integer'),
    Field('FirstSuccessful', 'integer'),
    migrate=False, primarykey=['UniqueId'])
UserTasks= semester.UserTasks

semester.define_table('SuccessfulTasks',
    Field('UserId','integer'),
    Field('TaskNr','integer'),
    migrate=False, primarykey = ['UserId', 'TaskNr'])
SuccessfulTasks= semester.SuccessfulTasks

semester.define_table('Whitelist',
    Field('UniqueId', 'integer', unique=True),
    Field('Email', 'string', unique=True),
    Field('Name', 'string'),
    migrate=False, primarykey=['UniqueId'])
Whitelist= semester.Whitelist

###################################################
##################### COURSE ######################
###################################################
course= DAL('sqlite://course.db')

course.define_table('SpecialMessages',
    Field('EventName', 'string',unique=True),
    Field('EventText', 'string'),
    migrate=False, primarykey=['EventName'])
SpecialMessages= course.SpecialMessages

course.define_table('TaskConfiguration',
    Field('TaskNr', 'integer'),
    Field('TaskStart', 'datetime'),
    Field('TaskDeadline', 'datetime'),
    Field('TaskName', 'string'),
    Field('GeneratorExecutable', 'string'),
    Field('TestExecutable', 'string'),
    Field('CommonFile','string'),
    Field('Score', 'integer'),
    Field('TaskOperator', 'string'),
    Field('TaskActive', 'integer'),
    migrate=False, primarykey=['TaskNr'])
TaskConfiguration= course.TaskConfiguration

course.define_table('GeneralConfig',
    Field('ConfigItem', 'string', unique=True),
    Field('Content', 'string'),
    migrate=False, primarykey=['ConfigItem'])
GeneralConfig= course.GeneralConfig
