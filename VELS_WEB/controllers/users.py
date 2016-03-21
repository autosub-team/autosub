val={'Name'        :[IS_NOT_EMPTY()],
     'Email'       :[IS_NOT_EMPTY(),IS_EMAIL()],
     'LastDone'    :[IS_EMPTY_OR(IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),error_message='must be YYYY-MM-DD HH:MM:SS!'))],
     'FirstMail'   :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),
                       error_message='must be YYYY-MM-DD HH:MM:SS!')],
     'CurrentTask' :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=1)]}

def __entries():
    rows=semester().select(Users.ALL)
    array=[]
    for row in rows:
        entry={'UserId'      :row.UserId,
               'Name'        :row.Name,
               'Email'       :row.Email,
               'LastDone'    :row.LastDone,
               'UserId'      :row.UserId,
               'FirstMail'   :row.FirstMail,
               'CurrentTask' :row.CurrentTask}
        array.append(entry)
    return dict(entries=array)


def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

def newUser():
    returnDict={}

    inputs=TD(INPUT(_name='Name',        requires= val['Name']        )),\
           TD(INPUT(_name='Email',       requires= val['Email']       ,_size="30")),\
           TD(INPUT(_name='FirstMail',   requires= val['FirstMail'],_placeholder="YYYY-MM-DD HH:MM:SS"   )),\
           TD(INPUT(_name='LastDone',    requires= val['LastDone'] ,_disabled='disabled'       )),\
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
                     LastDone        =form.vars.LastDone,
                     CurrentTask     =form.vars.CurrentTask)
        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

def deleteUser():
    UserId= request.vars['UserId']
    if semester(Users.UserId==UserId).delete() :
        msg='User' + UserId + ' deleted'
    else:
        msg='User' + UserId + ' delete failed'
    redirect(URL('index'))

def editUser():
    returnDict={}
    UserId= int(request.vars['editUserId'])
    entry=semester(Users.UserId==UserId).select(Users.ALL).first()
    inputs=TD(INPUT(_name='Name',        _value=entry.Name ,       requires=val['Name']        )),\
           TD(INPUT(_name='Email',       _value=entry.Email ,      requires=val['Email']       )),\
           TD(INPUT(_name='FirstMail',   _value=entry.FirstMail,   requires=val['FirstMail'], _placeholder="YYYY-MM-DD HH:MM:SS"  )),\
           TD(INPUT(_name='LastDone',    _value=entry.LastDone,    requires=val['LastDone'], _placeholder="Empty or DATETIME"    )),\
           TD(INPUT(_name='CurrentTask', _value=entry.CurrentTask, requires=val['CurrentTask'] )),\
           TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)

    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()
            
        semester(Users.UserId ==UserId).update(Name            =form.vars.Name,
                                               Email           =form.vars.Email,
                                               FirstMail       =form.vars.FirstMail,
                                               LastDone        =form.vars.LastDone,
                                               CurrentTask     =form.vars.CurrentTask)
        redirect(URL('index'))

    returnDict.update({'editUserId':UserId})
    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

def viewUser():
    returnDict={}
    UserId= int(request.vars['UserId'])

    row=semester(Users.UserId==UserId).select(Users.ALL).first()

    userInfoDict= {'UserId':UserId,
                   'Name':row.Name, 
                   'Email':row.Email,
                   'FirstMail':row.FirstMail,
                   'LastDone':row.LastDone,
                   'CurrentTask':row.CurrentTask}

    #user score
    rowsDoneTasks= semester(UserTasks.UserId == UserId, UserTasks.FirstSuccessful != None).select(UserTasks.TaskNr)
    userScore= 0

    for rowDoneTasks in rowsDoneTasks: 
        taskScore= course(TaskConfiguration.TaskNr == rowDoneTasks.TaskNr).select(TaskConfiguration.Score).first().Score
        userScore= userScore + taskScore 
   
    
    userInfoDict['UserScore']= userScore

    
    
    returnDict.update(dict(userInfo=userInfoDict))

    #Statistics for each task
    rows=semester(UserTasks.UserId==UserId).select(UserTasks.ALL,orderby=UserTasks.TaskNr)
    
    taskInfosArray=[]
    for row in rows:   
        taskInfosArray.append({'TaskNr':row.TaskNr, 
                     'NrSubmissions':row.NrSubmissions, 
                     'FirstSuccessful':row.FirstSuccessful,
                     'TaskAttachments':row.TaskAttachments.split()})
    
    returnDict.update(dict(taskInfos=taskInfosArray))
    
    return returnDict
