val={'registration_deadline' :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'),
                       error_message='must be YYYY-MM-DD HH:MM:SS!')],
     'num_tasks'             :[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(minimum=1)],
     'archive_dir'           :[IS_NOT_EMPTY()],
     'admin_email'           :[IS_NOT_EMPTY(),IS_EMAIL_LIST()],
     'challenge_mode'        :[IS_NOT_EMPTY(),IS_IN_SET(['normal','exam'])],
     'course_name'           :[IS_NOT_EMPTY()]}

def __entries():
    rows=course().select(GeneralConfig.ALL)
    entries={}
    for row in rows:
        entries.update({row.ConfigItem:row.Content})
    return dict(entries=entries)

def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

def edit():
    returnDict={}
    entries=__entries()['entries']
    inputs= TR(TD("Number of tasks"),       TD(INPUT(_name="num_tasks",             _value=entries['num_tasks'], requires=val['num_tasks']))) ,\
           TR(TD("Registration Deadline"), TD(INPUT(_name="registration_deadline", _placeholder="YYYY-MM-DD HH:MM:SS", _value=entries['registration_deadline'], requires=val['registration_deadline']))),\
           TR(TD("Archive Directory",      TD(INPUT(_name="archive_dir",           _value=entries['archive_dir'], requires=val['archive_dir'])))),\
           TR(TD("Administrator E-Mail", TD(INPUT(_name="admin_email", _value=entries['admin_email'], requires=val['admin_email'],_size="50")))),\
           TR(TD("Challenge Mode", TD(INPUT(_name="challenge_mode", _value=entries['challenge_mode'], requires=val['challenge_mode'],_size="10")))),\
           TR(TD("Course Name", TD(INPUT(_name="course_name", _value=entries['course_name'], requires=val['course_name'],_size="30")))),\
           TR(TD(INPUT(_type='submit',_label='Save'),_colspan=2))

    form= FORM(inputs)

    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()
            
        #get old and new num_tasks
        row=course(GeneralConfig.ConfigItem =='num_tasks').select(GeneralConfig.Content)[0]
        oldTaskNr=int(row.Content)
        newTaskNr=int(form.vars.num_tasks)

        course(GeneralConfig.ConfigItem =='num_tasks').update(Content=form.vars.num_tasks)
        course(GeneralConfig.ConfigItem =='archive_dir').update(Content=form.vars.archive_dir)
        course(GeneralConfig.ConfigItem =='registration_deadline').update(Content=form.vars.registration_deadline)
        course(GeneralConfig.ConfigItem =='admin_email').update(Content=form.vars.admin_email)
        course(GeneralConfig.ConfigItem =='challenge_mode').update(Content=form.vars.challenge_mode)
        course(GeneralConfig.ConfigItem =='course_name').update(Content=form.vars.course_name)
        

        #now adjust the TaskStats table
        if oldTaskNr>newTaskNr: #deletion needed
            semester(TaskStats.TaskId>newTaskNr ).delete()
        elif newTaskNr> oldTaskNr: #inserts needed
            for i in range(oldTaskNr+1,newTaskNr+1):
                TaskStats.insert(TaskId=i, NrSubmissions=0, NrSuccessful=0)

        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(entries)
    return returnDict
