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

import concurrent.futures
import logging
import threading
import time
import random 
import queue

class LoginInfo:
    def __init__(self, filename="user.txt"):
        emailAcctFile = open(filename, "r")
        self.HOSTNAME = emailAcctFile.readline().strip()
        self.USERNAME = emailAcctFile.readline().strip()
        self.PASSWORD = emailAcctFile.readline().strip()
        print(self.HOSTNAME + self.USERNAME)
        # Please use an app password


MAILBOX = 'Inbox'
NEWMAIL_OFFSET = 0 
MAIL_CHECK_FREQ = 20

# returns KV pair of datetime of email received date and email object 
def email_to_KV(email_obj):
    email_mktime = time.mktime(email.utils.parsedate(email_obj['Date']))
    return (email_mktime, email_obj)

# returns datetime (key) of KV pair
def extractDate(kv):
    return kv[0]

""" extract emails from IMAP server connection within messages and marks them as unread """
def extractEmailsFromIMAP(messages, email_list, server):
    email_ids = []
    for uid, message_data in server.fetch(messages, 'RFC822').items():
        email_message = email.message_from_bytes(message_data[b'RFC822'])
        email_ids.append(uid)
        email_list.append(email_to_KV(email_message))
    server.remove_flags(email_ids, [SEEN])

def startECR():

    acct = LoginInfo()

    try:
        print(acct.HOSTNAME + " " + acct.USERNAME + " " + acct.PASSWORD)
        server = IMAPClient(acct.HOSTNAME, use_uid=True, ssl=True)
        server.login(acct.USERNAME, acct.PASSWORD)
    except:
        connected = False
        print("ECR:: Error occurred while connecting")
    else:
        connected = True
        select_info = server.select_folder(MAILBOX)

    try:
        old_email_count = 0
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
                email_list = []

                # Extracting unread emails from IMAP Server 
                extractEmailsFromIMAP(messages, email_list, server)

                # sort by date received,newest 1st
                email_list.sort(reverse=True, key=extractDate)

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
                
                time.sleep(MAIL_CHECK_FREQ)
                old_email_count = newmails
    except KeyboardInterrupt:
        print("ECR::closing email client")
        server.logout()
