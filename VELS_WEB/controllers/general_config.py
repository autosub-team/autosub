import datetime

val={'registration_deadline' :[IS_NOT_EMPTY(),IS_DATETIME(format=T('%Y-%m-%d %H:%M'),
                       error_message='must be YYYY-MM-DD HH:MM!')],
     'archive_dir'           :[IS_NOT_EMPTY()],
     'admin_email'           :[IS_NOT_EMPTY(),IS_EMAIL_LIST()]}

def __entries():
    rows=course().select(GeneralConfig.ALL)
    entries={}
    for row in rows:
        if row.ConfigItem == 'registration_deadline':
            if row.Content == "NULL":
                entries.update({row.ConfigItem:"SET ME!!"})
            else:
                registration_deadline = datetime.datetime.strptime(row.Content, "%Y-%m-%d %H:%M:%S")
                entries.update({row.ConfigItem:registration_deadline.strftime("%Y-%m-%d %H:%M")})
        else:
            entries.update({row.ConfigItem:row.Content})

        if row.ConfigItem in ['allow_skipping', 'auto_advance']:
            if row.Content == "1":
                entries.update({row.ConfigItem: "True"})
            else:
                entries.update({row.ConfigItem: "False"})
    return dict(entries=entries)

def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

def edit():
    returnDict={}
    entries = __entries()['entries']
    inputs = TR(TD("Registration Deadline"), TD(INPUT(_name="registration_deadline", _placeholder="YYYY-MM-DD HH:MM", _value=entries['registration_deadline'], requires=val['registration_deadline'], _id='RegistrationDeadline'))),\
             TR(TD("Archive Directory",      TD(INPUT(_name="archive_dir",           _value=entries['archive_dir'], requires=val['archive_dir'])))),\
             TR(TD("Administrator E-Mail", TD(INPUT(_name="admin_email", _value=entries['admin_email'], requires=val['admin_email'],_size="50")))),\
             TR(TD(INPUT(_type='submit',_label='Save'),_colspan=2))

    form= FORM(inputs)

    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var=var.strip()

        course(GeneralConfig.ConfigItem =='archive_dir').update(Content=form.vars.archive_dir)
        course(GeneralConfig.ConfigItem =='registration_deadline').update(Content=form.vars.registration_deadline)
        course(GeneralConfig.ConfigItem =='admin_email').update(Content=form.vars.admin_email)

        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(entries)
    return returnDict
