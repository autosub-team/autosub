########################################################################
# commoon.py -- common functions
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################


####
# send_email()
####
def send_email(queue, recipient, userid, messagetype, tasknr, body, messageid):
   queue.put(dict({"recipient": recipient, "UserId": userid ,"message_type": messagetype, "Task": tasknr, "Body": body, "MessageId": messageid}))

