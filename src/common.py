

####
# send_email()
####
def send_email(queue, recipient, userid, messagetype, tasknr, body, messageid):
   queue.put(dict({"recipient": recipient, "UserId": userid ,"message_type": messagetype, "Task": tasknr, "Body": body, "MessageId": messageid}))

