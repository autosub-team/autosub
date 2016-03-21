def __entriesTaskStats():
    array=[]
    rows=semester().select(TaskStats.ALL)
    for row in rows:
        if(row.NrSuccessful==0 or row.NrSubmissions==0):
           percentage="0%";
        else:
           percentage=str(row.NrSuccessful*100/row.NrSubmissions)+"%"
        entry={'TaskId':row.TaskId,
               'NrSubmissions':row.NrSubmissions,
               'NrSuccessful':row.NrSuccessful,
               'Percentage':percentage}
        array.append(entry)
    return dict(entriesTaskStats=array)

def __entriesStatCounters():
    array=[]
    rows=semester().select(StatCounters.ALL, orderby=StatCounters.Name)
    for row in rows:
        entry={'CounterId'     :row.CounterId,
               'Name'          :row.Name,
               'Value'         :row.Value}
        array.append(entry)
    return dict(entriesStatCounters=array)

def index():
    returnDict={}
    returnDict.update(__entriesTaskStats())
    returnDict.update(__entriesStatCounters())
    return returnDict
