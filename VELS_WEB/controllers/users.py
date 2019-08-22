import cStringIO
import csv
from gluon.tools import Expose
import os

val={'Name'        :[IS_NOT_EMPTY()],
     'Email'       :[IS_NOT_EMPTY(),IS_EMAIL()],
     'LastDone'    :[IS_EMPTY_OR(IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),error_message='must be YYYY-MM-DD HH:MM:SS!'))],
     'RegisteredAt'   :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),
                       error_message='must be YYYY-MM-DD HH:MM:SS!')],
     'CurrentTask' :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=1)]}

def __entries():
    rows=semester().select(Users.ALL)
    array=[]
    for row in rows:

        rows_nrs = semester(SuccessfulTasks.UserId == row.UserId) \
                   .select(SuccessfulTasks.TaskNr, orderby="SuccessfulTasks.TaskNr ASC")

        if(len(rows_nrs) == 0):
            numFinished = 0
            finishedTasks = ""
        else:
            nrs = []
            for row_nrs in rows_nrs:
                nrs.append(str(row_nrs.TaskNr))
            numFinished = str(len(nrs))
            finishedTasks = ','.join(nrs)

        entry={'UserId'         : row.UserId,
               'Name'           : row.Name,
               'Email'          : row.Email,
               'NumFinished'    : numFinished,
               'FinishedTasks'  : finishedTasks,
               'LastDone'       : row.LastDone,
               'RegisteredAt'   : row.RegisteredAt,
               'CurrentTask'    : row.CurrentTask}
        array.append(entry)

    return dict(entries=array)

@auth.requires_permission('view data')
def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

@auth.requires_permission('view data')
def downloadAsCSV():
    download_file = cStringIO.StringIO()

    fields= ['UserId','Name','Email','NumFinished','FinishedTasks','CurrentTask','RegisteredAt','LastDone']
    csv_file = csv.DictWriter(download_file, delimiter = ';', fieldnames=fields)

    csv_file.writeheader()

    entries = __entries()['entries']
    for entry in entries:
        csv_file.writerow(entry)

    response.headers['Content-Type']='application/vnd.ms-excel'
    response.headers['Content-Disposition']='attachment; filename=VELS_users.csv'
    return download_file.getvalue()


@auth.requires_permission('edit data')
def newUser():
    returnDict={}

    inputs=TD(INPUT(_name='Name',        requires= val['Name']        )),\
           TD(INPUT(_name='Email',       requires= val['Email']       ,_size="30")),\
           TD(INPUT(_name='RegisteredAt',   requires= val['RegisteredAt'],_placeholder="YYYY-MM-DD HH:MM:SS"   )),\
           TD(INPUT(_name='CurrentTask', requires= val['CurrentTask'] )),\
           TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)

    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()

        Users.insert(Name            =form.vars.Name,
                     Email           =form.vars.Email,
                     FirstMail       =form.vars.FirstMail,
                     CurrentTask     =form.vars.CurrentTask)
        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

@auth.requires_permission('edit data')
def deleteUser():
    UserId= request.vars['UserId']
    if semester(Users.UserId==UserId).delete() :
        msg='User' + UserId + ' deleted'
    else:
        msg='User' + UserId + ' delete failed'
    redirect(URL('index'))

@auth.requires_permission('edit data')
def editUser():
    returnDict={}
    UserId= int(request.vars['editUserId'])
    entry=semester(Users.UserId==UserId).select(Users.ALL).first()
    inputs=TD(INPUT(_name='Name',        _value=entry.Name ,       requires=val['Name']        )),\
           TD(INPUT(_name='Email',       _value=entry.Email ,      requires=val['Email']       )),\
           TD(INPUT(_name='RegisteredAt',   _value=entry.RegisteredAt,
           requires=val['RegisteredAt'], _placeholder="YYYY-MM-DD HH:MM:SS"  )),\
           TD(INPUT(_name='CurrentTask', _value=entry.CurrentTask, requires=val['CurrentTask'] )),\
           TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)

    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()

        semester(Users.UserId ==UserId).update(Name             =form.vars.Name,
                                               Email            =form.vars.Email,
                                               RegisteredAt     =form.vars.RegisteredAt,
                                               CurrentTask      =form.vars.CurrentTask)
        redirect(URL('index'))

    returnDict.update({'editUserId':UserId})
    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

@auth.requires_permission('view data')
def viewUser():
    returnDict={}
    UserId= int(request.vars['UserId'])

    row=semester(Users.UserId==UserId).select(Users.ALL).first()

    userInfoDict= {'UserId':UserId,
                   'Name':row.Name,
                   'Email':row.Email,
                   'RegisteredAt':row.RegisteredAt,
                   'LastDone':row.LastDone,
                   'CurrentTask':row.CurrentTask}

    #TODO: Maybe one query for the whole score calculation?
    #user score
    rows_done_tasks= semester(SuccessfulTasks.UserId == UserId) \
                     .select(SuccessfulTasks.TaskNr, orderby="SuccessfulTasks.TaskNr ASC")

    done_tasks = [str(row.TaskNr) for row in rows_done_tasks]

    if not done_tasks:
        userScore = 0
    else:
        sql_string = '(' + ','.join(done_tasks) + ')'

        sql_cmd = "SELECT SUM(Score) FROM TaskConfiguration WHERE TaskNr in {0} " \
                  .format(sql_string)
        res = course.executesql(sql_cmd)
        userScore = res[0][0]

    userInfoDict['UserScore']= userScore

    #TODO: Merge with above queries
    # user successful tasks
    rows_nrs = semester(SuccessfulTasks.UserId == UserId) \
               .select(SuccessfulTasks.TaskNr, orderby="SuccessfulTasks.TaskNr ASC")

    if(len(rows_nrs) == 0):
        numFinished = 0
        finishedTasks = ""
    else:
        nrs = []
        for row_nrs in rows_nrs:
            nrs.append(str(row_nrs.TaskNr))
        numFinished = str(len(nrs))
        finishedTasks = ','.join(nrs)

    userInfoDict['UserNumFinished']= numFinished
    userInfoDict['UserFinishedTasks'] = finishedTasks

    # assemble the returnDict
    returnDict.update(dict(userInfo=userInfoDict))

    #Statistics for each task
    rows=semester(UserTasks.UserId==UserId).select(UserTasks.ALL,orderby=UserTasks.TaskNr)

    taskInfosArray=[]
    for row in rows:
        row_taskconfig= \
            course(TaskConfiguration.TaskNr==row.TaskNr).select(TaskConfiguration.ALL).first()
        taskInfosArray.append({'TaskNr':row.TaskNr,
                     'NrSubmissions':row.NrSubmissions,
                     'FirstSuccessful':row.FirstSuccessful,
                     'TaskName' : row_taskconfig.TaskName})

    returnDict.update(dict(taskInfos=taskInfosArray))

    return returnDict

@auth.requires_permission('view data')
def viewUserTaskFolder():
    if not request.get_vars['UserId']:
        UserId = session.viewUserId
    else:
        UserId= int(request.get_vars['UserId'])
        session.viewUserId = UserId

    if not request.vars['TaskNr']:
        TaskNr = session.viewTaskNr
    else:
        TaskNr= int(request.vars['TaskNr'])
        session.viewTaskNr = TaskNr

    row = semester(Users.UserId == UserId).select(Users.Name).first()
    Name = row['Name']

    usersDir="/home/vels/autosub/src/users"

    taskSubDir = "{0}/Task{1}".format(UserId, TaskNr)
    absoluteDir = os.path.join(usersDir, taskSubDir)

    return dict(files=Expose(base=absoluteDir, basename="basefolder"), TaskNr=TaskNr, Name=Name, UserId=UserId)
