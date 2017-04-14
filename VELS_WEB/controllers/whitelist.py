val={ 'Email':[IS_NOT_EMPTY(), IS_EMAIL()] ,
      'EmailMass':[IS_NOT_EMPTY(), IS_EMAIL_MASS()]}

def __entries():
    rows= semester().select(Whitelist.ALL)
    array= []
    for row in rows:
        entry= {'UniqueId'    :row.UniqueId,
                'Email'       :row.Email,
                'Name'        :row.Name}
        array.append(entry)
    return dict(entries=array)

def index():
    returnDict= {}
    returnDict.update(__entries())
    return returnDict

def newEmail():
    returnDict= {}

    inputs= TD( INPUT(_name='Email', _size="30", _placeholder=" User Email", requires= val['Email']) ),\
            TD( INPUT(_name='Name', _size="30", _placeholder=" User Name") ),\
            TD( INPUT(_type='submit', _label='Save') )
    form= FORM(inputs)

    if(form.process().accepted):
        #strip all whitespaces from begin and end
        for var in form.vars:
            var= var.strip().strip('\r')
        Whitelist.insert(Email= form.vars.Email, Name=form.vars.Name)
        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

def deleteEmail():
    UniqueId= request.vars['UniqueId']
    if semester(Whitelist.UniqueId==UniqueId).delete() :
        msg= 'Email deleted'
    else:
        msg= 'Email delete failed'
    redirect(URL('index'))
    
def massEmail():
    returnDict= {}

    inputs= TR(TD(TEXTAREA(_name='EmailMass', requires=val['EmailMass'],_cols="60",_rows="30"))),\
            TR(TD(INPUT(_type='submit',_label='Save')))
    form= FORM(inputs)
    if form.process().accepted:
        lines = form.vars.EmailMass.split('\n')
        for line in lines:
            line= line.strip("\r ")
            elements = line.split(';')
            email= elements[0].strip()

            #the name is optional
            if len(elements) > 1:
                name= elements[1].strip()
            else:
                name= ""
            Whitelist.insert(Email=email, Name=name)

        redirect(URL('index'))

    returnDict.update({'form':form})
    return returnDict
