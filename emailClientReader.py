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
import random 
import queue


class LoginInfo:
    def __init__(self, filename="user.txt"):
        emailAcctFile = open(filename, "r")
        self.HOSTNAME = emailAcctFile.readline().strip()
        self.USERNAME = emailAcctFile.readline().strip()
        self.PASSWORD = emailAcctFile.readline().strip()
        # Please use an app password



class ECR:
    MAILBOX = 'Inbox'

    def __init__(self, email_queue, end_event, logging, check_freq = 20):
        self.queue = email_queue
        self.end_event = end_event
        self.logging = logging
        self.check_freq = check_freq

    """returns KV pair of datetime of email received date and email object"""
    def email_to_KV(email_obj):
        email_mktime = time.mktime(email.utils.parsedate(email_obj['Date']))
        return (email_mktime, email_obj)

    """ returns datetime (key) of KV pair"""
    def extractDate(kv):
        return kv[0]

    """ extract emails from IMAP server connection within messages and marks them as unread """
    def extractEmailsFromIMAP(messages, email_list, server):
        email_ids = []
        for uid, message_data in server.fetch(messages, 'RFC822').items():
            email_message = email.message_from_bytes(message_data[b'RFC822'])
            email_ids.append(uid)
            email_list.append(ECR.email_to_KV(email_message))
        server.remove_flags(email_ids, [SEEN])

    def startECR(self):
        # Read user's email account info in user.txt
        acct = LoginInfo() 

        try:
            #print(acct.HOSTNAME + " " + acct.USERNAME + " " + acct.PASSWORD)
            server = IMAPClient(acct.HOSTNAME, use_uid=True, ssl=True)
            server.login(acct.USERNAME, acct.PASSWORD)
        except:
            connected = False
            self.logging.info("ECR:: Error occurred while connecting")
            return
        
        connected = True
        select_info = server.select_folder(ECR.MAILBOX)
        self.logging.info("ECR connected")

        try:
            old_email_count = 0
            self.logging.info("endEvent, isSet =" + str(self.end_event.is_set()))
            while(connected and not self.end_event.is_set()):
                self.logging.info("ECR connected")
                folder_status = server.folder_status(ECR.MAILBOX, 'UNSEEN')
                #print("folder status info" + str(folder_status))
                newmails = int(folder_status[b'UNSEEN'])
                if(old_email_count > newmails):#client has deleted some of their old mail, reset count
                    old_email_count = 0
                elif(old_email_count == newmails):#no new email to output
                    pass
                    #print("no new emails to output")
                else:
                    delta = newmails - old_email_count
                    messages = server.search('UNSEEN')
                    last_check = datetime.datetime.now()
                    email_list = []

                    # Extracting unread emails from IMAP Server 
                    ECR.extractEmailsFromIMAP(messages, email_list, server)

                    # sort by date received,newest 1st
                    email_list.sort(reverse=True, key=ECR.extractDate)

                    # implicit filtering, only read delta emails
                    for i in range(delta):
                        email_obj = email_list[i][1]
                        email_subj = email_obj.get('Subject')
                        email_from = email_obj.get('From')
                        email_body = None
                        email_multipart = []
                        if(email_obj.is_multipart()):
                            for payload in email_obj.get_payload():
                                email_multipart.append(payload.get_payload())
                        else:
                            email_body = email_obj.get_payload()
                        email_tuple = (email_subj, email_from, email_multipart, email_body)
                        self.queue.put(email_tuple)
                        self.logging.info("ECR placed email content " + email_subj)

                    #print("---------end implicit email list-----------")
                    # Marking extracted emails as unread
                    
                    time.sleep(self.check_freq)
                    old_email_count = newmails
        except KeyboardInterrupt:
            self.logging("ECR::closing email client")
            self.end_event.set()
            server.logout()
