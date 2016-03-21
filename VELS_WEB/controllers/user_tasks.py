def __entries():
    rows=semester().select(UserTasks.ALL)
    array=[]
    for row in rows:
        entry={'UniqueId'         :row.UniqueId,
               'TaskNr'           :row.TaskNr,
                'UserId'          :row.UserId,
                'TaskParameters'  :row.TaskParameters,
                'TaskDescription' :row.TaskDescription,
                'TaskAttachments' :row.TaskAttachments,
                'NrSubmissions'   :row.NrSubmissions,
                'FirstSuccessful' :row.FirstSuccessful}
        array.append(entry)
    return dict(entries=array)

def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict
