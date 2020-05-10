#!/usr/bin/python

"""
 Prints new emails as they come in

 Things to consider in the future:
  include date filtering so sorting and filtering logic doesn't need to deal with same old unread emails per iteration
  provide support to sample from multiple IMAPClients (for multiple emails)
"""
from imapclient import IMAPClient, SEEN
import time
import sys
import email
import datetime

HOSTNAME = 'imap.gmail.com'
USERNAME = 'sih28@cornell.edu'
passwordFile = open("user.txt","r")
PASSWORD =  passwordFile.read() #have it read an encrypted file w/ password
MAILBOX = 'Inbox'
NEWMAIL_OFFSET = 0 
MAIL_CHECK_FREQ = 20
old_email_count = 0

# returns KV pair of datetime of email received date and email object 
def email_to_KV(email_obj):
    #print("emailToKV("+str(email_obj)+")")
    #print(type(email_obj))
    email_mktime = time.mktime(email.utils.parsedate(email_obj['Date']))
    return (email_mktime, email_obj)

# returns datetime (key) of KV pair
def extractDate(kv):
    return kv[0]

ReadEmailIds = []

try:
    server = IMAPClient(HOSTNAME, use_uid=True, ssl=True)
    server.login(USERNAME, PASSWORD)
except:
    connected = False
    print("ECR:: Error occurred while connecting")
else:
    connected = True
    #print("Successful connection")
    select_info = server.select_folder(MAILBOX)

try:
    while(connected):
        last_check = None
        folder_status = server.folder_status(MAILBOX, 'UNSEEN')
        #print("folder status info" + str(folder_status))
        newmails = int(folder_status[b'UNSEEN'])
        if(old_email_count > newmails):#client has deleted some of their old mail, reset count
            old_email_count = 0
        elif(old_email_count == newmails):#no new email to output
            #print("no new emails to output")
            time.sleep(MAIL_CHECK_FREQ)
        else:
            delta = newmails - old_email_count
            messages = server.search('UNSEEN')
            last_check = datetime.datetime.now()
            #print("reading " + str(delta) + " emails")
            email_list = []

            # Extracting emails from IMAP Server
            for uid, message_data in server.fetch(messages, 'RFC822').items():
                email_message = email.message_from_bytes(message_data[b'RFC822'])
                #print("DEBUG, email msg contents " + str(email_message))
                #print(uid, email_message.get('From'), email_message.get('Subject'))
                ReadEmailIds.append(uid)
                email_list.append(email_to_KV(email_message))

            # sort by date received,newest 1st
            # email_list.sort(reverse=True, key=extractDate)

            # implicit filtering, only read delta emails
            #print("--------begin implicit email list----------")
            for i in range(delta):
                email_obj = email_list[i][1]
                print(email_obj.get('Subject'))
                print(email_obj.get('From'))
                if(email_obj.is_multipart()):
                    for payload in email_obj.get_payload():
                        print(payload.get_payload())
                else:
                    print(email_obj.get_payload())
            #print("---------end implicit email list-----------")
            # Marking extracted emails as unread
            server.remove_flags(ReadEmailIds, [SEEN])
            time.sleep(MAIL_CHECK_FREQ)
            old_email_count = newmails
except KeyboardInterrupt:
    print("ECR::closing email client")
    server.logout()
