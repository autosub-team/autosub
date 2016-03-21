val={   'WELCOME'    :[IS_NOT_EMPTY()],
        'USAGE'      :[IS_NOT_EMPTY()],
        'QUESTION'   :[IS_NOT_EMPTY()],
        'INVALID'    :[IS_NOT_EMPTY()],
        'CONGRATS'   :[IS_NOT_EMPTY()],
        'REGOVER'    :[IS_NOT_EMPTY()],
        'NOTALLOWED' :[IS_NOT_EMPTY()],
        'CURLAST'    :[IS_NOT_EMPTY()],
        'DEADTASK'   :[IS_NOT_EMPTY()]}

def __entries():
    rows=course().select(SpecialMessages.ALL)
    entries={}
    for row in rows:
        entries.update({row.EventName:row.EventText})
    return dict(entries=entries)

def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

def edit():
    returnDict={}
    entries=__entries()['entries']
    inputs=TR(TD("WELCOME"),     TD(TEXTAREA(entries['WELCOME']    ,_name='WELCOME'    ,_cols="80", requires=val['WELCOME']))) ,\
           TR(TD("USAGE"),       TD(TEXTAREA(entries['USAGE']      ,_name='USAGE'      ,_cols="80", requires=val['USAGE']))) ,\
           TR(TD("QUESTION"),    TD(TEXTAREA(entries['QUESTION']   ,_name='QUESTION'   ,_cols="80", requires=val['QUESTION']))) ,\
           TR(TD("INVALID"),     TD(TEXTAREA(entries['INVALID']    ,_name='INVALID'    ,_cols="80", requires=val['INVALID']))) ,\
           TR(TD("CONGRATS"),    TD(TEXTAREA(entries['CONGRATS']   ,_name='CONGRATS'   ,_cols="80", requires=val['CONGRATS']))) ,\
           TR(TD("REGOVER"),     TD(TEXTAREA(entries['REGOVER']    ,_name='REGOVER'    ,_cols="80", requires=val['REGOVER']))) ,\
           TR(TD("NOTALLOWED"),  TD(TEXTAREA(entries['NOTALLOWED'] ,_name='NOTALLOWED' ,_cols="80", requires=val['NOTALLOWED']))) ,\
           TR(TD("CURLAST"),     TD(TEXTAREA(entries['CURLAST']    ,_name='CURLAST'    ,_cols="80", requires=val['CURLAST']))) ,\
           TR(TD("DEADTASK"),    TD(TEXTAREA(entries['DEADTASK']   ,_name='DEADTASK'   ,_cols="80", requires=val['DEADTASK']))) ,\
           TR(TD(INPUT(_type='submit',_label='Save'),_colspan=2))

    form= FORM(inputs)

    if(form.process().accepted):
        course(SpecialMessages.EventName =='WELCOME').update(EventText=form.vars.WELCOME)
        course(SpecialMessages.EventName =='USAGE').update(EventText=form.vars.USAGE)
        course(SpecialMessages.EventName =='QUESTION').update(EventText=form.vars.QUESTION)
        course(SpecialMessages.EventName =='INVALID').update(EventText=form.vars.INVALID)
        course(SpecialMessages.EventName =='CONGRATS').update(EventText=form.vars.CONGRATS)
        course(SpecialMessages.EventName =='REGOVER').update(EventText=form.vars.REGOVER)
        course(SpecialMessages.EventName =='NOTALLOWED').update(EventText=form.vars.NOTALLOWED)
        course(SpecialMessages.EventName =='CURLAST').update(EventText=form.vars.CURLAST)
        course(SpecialMessages.EventName =='DEADTASK').update(EventText=form.vars.DEADTASK)
        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(entries)
    return returnDict
