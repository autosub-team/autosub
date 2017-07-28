from os.path import isdir
from os.path import isfile
import os
import datetime

#Validators
#TaskName, CommonFile, TestExecutable, GeneratorExecutable get validated with extra_validation
val={'TaskNr'              :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=0)],
     'TaskStart'           :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M'), \
                             error_message='must be YYYY-MM-DD HH:MM!')],
     'TaskDeadline'        :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M'), \
                             error_message='must be YYYY-MM-DD HH:MM!')],
     'Score'               :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=1)],
     'TaskOperator'        :[IS_NOT_EMPTY(),IS_EMAIL_LIST()],
     'TaskActive'          :[IS_NOT_EMPTY(),IS_IN_SET(['0','1'])]}

def extra_validation(form):
    # get the configured tasks directory
    tasks_dir = course(GeneralConfig.ConfigItem=='tasks_dir').select(GeneralConfig.Content)[0].Content

    available_tasks = sorted(next(os.walk(tasks_dir))[1])
    if '_common' in available_tasks:
        available_tasks.remove('_common')

    #validate TaskName, has tom exist in tasks_dir
    if form.vars.TaskName not in available_tasks:
        form.errors.TaskName = 'task does not exist'
        return

    #validate CommonFile, has to be empty or in tasks_dir/_common/
    common_file = form.vars.CommonFile.strip()

    if not common_file:
        pass
    else:
        full_path = tasks_dir + "/_common/" + common_file
        if not isfile(full_path):
            form.errors.CommomFile = "file does not exist!"
            return

    task_path = tasks_dir + '/' + form.vars.TaskName

    #validate GeneratorExecutable
    full_path = task_path + "/" + form.vars.GeneratorExecutable

    if not isfile(full_path):
        form.errors.GeneratorExecutable = "file does not exist!"

    #validate TestExecutable
    full_path = task_path + "/" + form.vars.TestExecutable

    if not isfile(full_path):
        form.errors.TestExecutable = "file does not exist!"

def __entries():
    rows=course().select(TaskConfiguration.ALL, orderby=TaskConfiguration.TaskNr)
    array=[]

    for row in rows:
        entry={'TaskNr'              :row.TaskNr,
               'TaskStart'           :row.TaskStart.strftime("%Y-%m-%d %H:%M"),
               'TaskDeadline'        :row.TaskDeadline.strftime("%Y-%m-%d %H:%M"),
               'TaskName'            :row.TaskName,
               'GeneratorExecutable' :row.GeneratorExecutable,
               'TestExecutable'      :row.TestExecutable,
               'CommonFile'          :"" if not row.CommonFile else row.CommonFile,
               'Score'               :row.Score,
               'TaskOperator'        :row.TaskOperator,
               'TaskActive'          :"Yes" if row.TaskActive else "No"}
        array.append(entry)

    tasks_dir = course(GeneralConfig.ConfigItem=='tasks_dir').select(GeneralConfig.Content)[0].Content

    if not os.path.isdir(tasks_dir):
        num_found_tasks = "Invalid Path."
    else:
        # only take subfolders not files of tasks_dir
        available_tasks = sorted([d for d in os.listdir(tasks_dir) 
                          if os.path.isdir(os.path.join(tasks_dir, d))])

        # delete _common out of it 
        if '_common' in available_tasks:
            available_tasks.remove('_common')
        num_found_tasks = str(len(available_tasks)) + " task(s) found."

    return dict(entries=array, tasks_dir = tasks_dir,
                num_found_tasks = num_found_tasks)


def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

def newTask():
    returnDict={}
    returnDict.update(__entries())

    #find next task nr (max() does not work..)
    rows=course().select(TaskConfiguration.TaskNr,orderby=TaskConfiguration.TaskNr)
    if len(rows)==0 :
        newTaskNr=1
    else:
        newTaskNr=rows.last().TaskNr+1
    returnDict.update({'newTaskNr': newTaskNr})

    # get the configured tasks directory
    tasks_dir = course(GeneralConfig.ConfigItem=='tasks_dir').select(GeneralConfig.Content)[0].Content

    available_tasks = [""]
    available_commons = [""]

    if os.path.isdir(tasks_dir):
        # only take subfolders not files of tasks_dir
        available_tasks = sorted([d for d in os.listdir(tasks_dir) 
                          if os.path.isdir(os.path.join(tasks_dir, d))])
 
        if '_common' in available_tasks:
            # delete _common out of it
            available_tasks.remove('_common')
            available_commons.extend(sorted(os.listdir(tasks_dir + "/_common")))

    inputs = TD(newTaskNr,INPUT(_type='hidden',_name='TaskNr',_value=newTaskNr)),\
             TD(INPUT(_name='TaskStart', requires=val['TaskStart'],\
                      _placeholder="YYYY-MM-DD HH:MM", _id = 'TaskStart')),\
             TD(INPUT(_name='TaskDeadline', requires=val['TaskDeadline'],\
                      _placeholder="YYYY-MM-DD HH:MM",_id = 'TaskEnd')),\
             TD(SELECT(_name="TaskName", *available_tasks)),\
             TD(INPUT(_name='GeneratorExecutable', _value="generator.sh")),\
             TD(INPUT(_name='TestExecutable', _value="tester.sh")),\
             TD(SELECT(_name='CommonFile', *available_commons, _value="")),\
             TD(INPUT(_name='Score', requires=val['Score'], _value=1)),\
             TD(INPUT(_name='TaskOperator', requires=val['TaskOperator'],\
                      _placeholder="Email")),\
             TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)

    if(form.process(onvalidation=extra_validation).accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var = var.strip()

        #Set TaskActive based on the StartTime
        if(form.vars.TaskStart < datetime.datetime.now()):
            TaskActive = 1;
        else:
            TaskActive = 0;

        TaskConfiguration.insert(TaskNr              =form.vars.TaskNr,\
                                 TaskStart           =form.vars.TaskStart,\
                                 TaskDeadline        =form.vars.TaskDeadline,\
                                 TaskName            =form.vars.TaskName,\
                                 GeneratorExecutable =form.vars.GeneratorExecutable,\
                                 TestExecutable      =form.vars.TestExecutable,\
                                 CommonFile          =form.vars.CommonFile,\
                                 Score               =form.vars.Score,\
                                 TaskOperator        =form.vars.TaskOperator,\
                                 TaskActive          =TaskActive)

        # add a entry in TaskStats
        TaskStats.insert(TaskId=form.vars.TaskNr,
                          NrSubmissions=0,
                          NrSuccessful=0)

        redirect(URL('index'))

    returnDict.update({'form':form})
    return returnDict

def editTask():
    returnDict={}
    returnDict.update(__entries())

    TaskNr = int(request.vars['editTaskNr'])
    entry =returnDict['entries'][TaskNr-1]

    # get the configured tasks directory
    tasks_dir = course(GeneralConfig.ConfigItem=='tasks_dir').select(GeneralConfig.Content)[0].Content

    available_tasks = sorted(next(os.walk(tasks_dir))[1])
    if '_common' in available_tasks:
        available_tasks.remove('_common')

    available_commons = [""]
    if isdir(tasks_dir + "/_common"):
        available_commons.extend(sorted(next(os.walk(tasks_dir + "/_common"))[2]))

    inputs = TD(TaskNr),\
             TD(INPUT(_name='TaskStart', _value=entry['TaskStart'],\
                      requires=val['TaskStart'], _id ='TaskStart', )),\
             TD(INPUT(_name='TaskDeadline', _value=entry['TaskDeadline'],\
                      requires=val['TaskDeadline'], _id = 'TaskEnd')),\
             TD(SELECT(_name="TaskName", value = entry['TaskName'],\
                       *available_tasks)),\
             TD(INPUT(_name='GeneratorExecutable', _value=entry['GeneratorExecutable'])),\
             TD(INPUT(_name='TestExecutable', _value=entry['TestExecutable'])),\
             TD(SELECT(_name='CommonFile', *available_commons, value=entry['CommonFile'])),\
             TD(INPUT(_name='Score',_value=entry['Score'],\
                      requires=val['Score'])),\
             TD(INPUT(_name='TaskOperator', _value=entry['TaskOperator'],\
                      requires=val['TaskOperator'], _placeholder="Email")),\
             TD(INPUT(_type='submit',_label='Save'))
    form = FORM(inputs)

    if(form.process(onvalidation=extra_validation).accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()

        #Set TaskActive based on the StartTime
        if(form.vars.TaskStart < datetime.datetime.now()):
            TaskActive = 1;
        else:
            TaskActive = 0;

        course(TaskConfiguration.TaskNr ==TaskNr).update(\
                    TaskStart           =form.vars.TaskStart,\
                    TaskDeadline        =form.vars.TaskDeadline,\
                    TaskName            =form.vars.TaskName,\
                    GeneratorExecutable =form.vars.GeneratorExecutable,\
                    TestExecutable      =form.vars.TestExecutable,\
                    CommonFile          =form.vars.CommonFile,\
                    Score               =form.vars.Score,\
                    TaskOperator        =form.vars.TaskOperator,\
                    TaskActive          =TaskActive)

        redirect(URL('index'))

    returnDict.update({'editTaskNr':TaskNr,'form':form})
    return returnDict

def deleteTask():
    TaskNr = request.vars['TaskNr']

    if course(TaskConfiguration.TaskNr==TaskNr).delete() :
        msg ='Task with number' + TaskNr + ' deleted'
    else:
        msg ='Deletion of Task with number ' + TaskNr + ' failed'

    # also delete the TaskStats entry
    semester(TaskStats.TaskId==TaskNr).delete()

    redirect(URL('index'))
