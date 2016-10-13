from os.path import expanduser
from os.path import isdir

#Validators
val={'TaskNr'              :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=0)],
     'TaskStart'           :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),
                       error_message='must be YYYY-MM-DD HH:MM:SS!')],
     'TaskDeadline'        :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),
                       error_message='must be YYYY-MM-DD HH:MM:SS!')],
     'PathToTask'          :[IS_NOT_EMPTY(),PATH_EXISTS()],
     'GeneratorExecutable' :[IS_NOT_EMPTY()],
     'TestExecutable'      :[IS_NOT_EMPTY()],
     'Score'               :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=1)],
     'TaskOperator'        :[IS_NOT_EMPTY(),IS_EMAIL_LIST()],
     'TaskActive'          :[IS_NOT_EMPTY(),IS_IN_SET(['0','1'])]}

def __entries():
    rows=course().select(TaskConfiguration.ALL,orderby=TaskConfiguration.TaskNr)
    array=[]
    for row in rows:
        entry={'TaskNr'              :row.TaskNr,
               'TaskStart'           :row.TaskStart,
               'TaskDeadline'        :row.TaskDeadline,
               'PathToTask'          :row.PathToTask,
               'GeneratorExecutable' :row.GeneratorExecutable,
               'TestExecutable'      :row.TestExecutable,
               'Score'               :row.Score,
               'TaskOperator'        :row.TaskOperator,
               'TaskActive'          :row.TaskActive}
        array.append(entry)
    return dict(entries=array)


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

    # guess for path of tasks
    task_path = str(expanduser("~")) + "/autosub/src/tasks/implementation/"

    #reset it to empty if that is not a existing path
    if(isdir(task_path)==False):
        task_path = ""

    inputs= TD(newTaskNr,INPUT(_type='hidden',_name='TaskNr',_value=newTaskNr) ),\
            TD(INPUT(_name='TaskStart',           requires=val['TaskStart']           , _placeholder="YYYY-MM-DD HH:MM:SS"                      )),\
            TD(INPUT(_name='TaskDeadline',        requires=val['TaskDeadline']        , _placeholder="YYYY-MM-DD HH:MM:SS"                      )),\
            TD(INPUT(_name='PathToTask',          requires=val['PathToTask']          , _placeholder="Path without ending /", _value = task_path)),\
            TD(INPUT(_name='GeneratorExecutable', requires=val['GeneratorExecutable'],  _value="generator.sh"                                   )),\
            TD(INPUT(_name='TestExecutable',      requires=val['TestExecutable'],       _value="tester.sh"                                      )),\
            TD(INPUT(_name='Score',               requires=val['Score'],                _value=1                                                )),\
            TD(INPUT(_name='TaskOperator',        requires=val['TaskOperator'],         _placeholder="Email"                                    )),\
            TD(INPUT(_name='TaskActive',          requires=val['TaskActive'],           _placeholder="1/0"                                      )),\
            TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)
    
    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()
            
        TaskConfiguration.insert(TaskNr              =form.vars.TaskNr,\
                                 TaskStart           =form.vars.TaskStart,\
                                 TaskDeadline        =form.vars.TaskDeadline,\
                                 PathToTask          =form.vars.PathToTask.rstrip("/"),\
                                 GeneratorExecutable =form.vars.GeneratorExecutable,\
                                 TestExecutable      =form.vars.TestExecutable,\
                                 Score               =form.vars.Score,\
                                 TaskOperator        =form.vars.TaskOperator,\
                                 TaskActive          =form.vars.TaskActive)
        redirect(URL('index'))

    returnDict.update({'form':form})
    return returnDict

def editTask():
    returnDict={}
    returnDict.update(__entries())
    TaskNr= int(request.vars['editTaskNr'])
    entry=returnDict['entries'][TaskNr-1]
    inputs=TD(TaskNr),\
           TD(INPUT(_name='TaskStart',           _value=entry['TaskStart'] ,          requires=val['TaskStart']           )),\
           TD(INPUT(_name='TaskDeadline',        _value=entry['TaskDeadline'] ,       requires=val['TaskDeadline']        )),\
           TD(INPUT(_name='PathToTask',          _value=entry['PathToTask'] ,         requires=val['PathToTask']          )),\
           TD(INPUT(_name='GeneratorExecutable', _value=entry['GeneratorExecutable'], requires=val['GeneratorExecutable'] )),\
           TD(INPUT(_name='TestExecutable',      _value=entry['TestExecutable'] ,     requires=val['TestExecutable']      )),\
           TD(INPUT(_name='Score',               _value=entry['Score'] ,              requires=val['Score']               )),\
           TD(INPUT(_name='TaskOperator',        _value=entry['TaskOperator'] ,       requires=val['TaskOperator']        )),\
           TD(INPUT(_name='TaskActive',        _value=entry['TaskActive'] ,       requires=val['TaskActive']        )),\
           TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)
    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()
            
        course(TaskConfiguration.TaskNr ==TaskNr).update(TaskStart           =form.vars.TaskStart,\
                                                         TaskDeadline        =form.vars.TaskDeadline,\
                                                         PathToTask          =form.vars.PathToTask.rstrip("/"),\
                                                         GeneratorExecutable =form.vars.GeneratorExecutable,\
                                                         TestExecutable      =form.vars.TestExecutable,\
                                                         Score               =form.vars.Score,\
                                                         TaskOperator        =form.vars.TaskOperator,\
                                                         TaskActive          =form.vars.TaskActive)
        redirect(URL('index'))

    returnDict.update({'editTaskNr':TaskNr,'form':form})
    return returnDict

def deleteTask():
    TaskNr= request.vars['TaskNr']
    if course(TaskConfiguration.TaskNr==TaskNr).delete() :
        msg='Task with number' + TaskNr + ' deleted'
    else:
        msg='Deletion of Task with number'+TaskNr+' failed'
    redirect(URL('index'))

def posSwitchDown():
    TaskNr= int(request.vars['TaskNr'])
    if(course(TaskConfiguration.TaskNr>TaskNr).count()>0): #switch possible?
        course(TaskConfiguration.TaskNr==TaskNr).update(TaskNr=0)
        course(TaskConfiguration.TaskNr==TaskNr+1).update(TaskNr=TaskNr)
        course(TaskConfiguration.TaskNr==0).update(TaskNr=TaskNr+1)
    redirect(URL('index'))

def posSwitchUp():
    TaskNr= int(request.vars['TaskNr'])
    if(course(TaskConfiguration.TaskNr<TaskNr).count()>0): #switch possible?
        course(TaskConfiguration.TaskNr==TaskNr).update(TaskNr=0)
        course(TaskConfiguration.TaskNr==TaskNr-1).update(TaskNr=TaskNr)
        course(TaskConfiguration.TaskNr==0).update(TaskNr=TaskNr-1)
    redirect(URL('index'))
