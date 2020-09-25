#!/usr/bin/python

"""
 Prints new emails as they come in

 Things to consider in the future:
  include date filtering so sorting and filtering logic doesn't need to deal with same old unread emails per iteration
  provide support to sample from multiple IMAPClients (for multiple emails)
"""
from imapclient import IMAPClient, SEEN
import time
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
        emailAcctFile.close()
        # Please use an app password



class ECR:
    MAILBOX = 'Inbox'

    def __init__(self, email_queue, end_event, logging, check_freq = 20):
        self.queue = email_queue
        self.end_event = end_event
        self.logging = logging
        self.check_freq = check_freq
        self.to_mark_unread = []
        self.processed_msgs = []
        self.connected = False
        try:
            self.acct = LoginInfo() 
            self.server = IMAPClient(self.acct.HOSTNAME, use_uid=True, ssl=True)
            self.server.login(self.acct.USERNAME, self.acct.PASSWORD)
            self.connected = True
        except:
            self.logging.info("ECR:: Error occurred while connecting")

    def reconnect(self, refresh_acct_args=False):
        try:
            self.connected = False
            if(refresh_acct_args):
                self.acct = LoginInfo()
            self.server = IMAPClient(self.acct.HOSTNAME, use_uid=True, ssl=True)
            self.server.login(self.acct.USERNAME, self.acct.PASSWORD)
            self.connected = True
        except:
            self.logging.info("ECR:: Error occurred while connecting")
        
    def shutdown(self):
        self.server.logout()
        self.connected = False

    """returns KV pair of msg-id of email and email object"""
    def email_to_KV(email_obj):
        msg_id = email_obj['Message-ID']
        return (msg_id, email_obj)

    """ returns msg-id (key) of KV pair"""
    def extract_msg_id(kv):
        return kv[0]

    """ returns email object (value) of KV pair"""
    def extract_email(kv):
        return kv[1]

    """ returns True if the message-id hasn't been processed before, false otherwise """
    def is_not_processed(self, email_kv):
        if ECR.extract_msg_id(email_kv) not in self.processed_msgs:
            return True
        else:
            return False

    """ extract emails from IMAP server connection within messages to the email_list and marks them as unread """
    def extract_emails_from_IMAP(self, messages, email_list):
        # flag = 'BODY.PEEK[]'
        flag = 'RFC822'
        flag_w_paren = '(' + flag + ')'
        # flag_b = b'BODY.PEEK[]'
        flag_b = b'RFC822'
        for uid, message_data in self.server.fetch(messages, flag).items():
            if( not (flag_b in message_data)):
                continue
            email_message = email.message_from_string(message_data[flag_b].decode())
            self.to_mark_unread.append(uid)
            email_list.append(ECR.email_to_KV(email_message))
        self.server.remove_flags(self.to_mark_unread, [SEEN])
        self.to_mark_unread = []

    """ blocking put() for queue unless end_event occurs """
    def put_email_in_queue(self,email_tuple):
        while(not self.end_event.is_set()):
            try:
                self.queue.put(email_tuple, block=False)
                break
            except queue.FULL as e:
                pass #try again
                


    def startECR(self):
        # Read user's email account info in user.txt
        try:
            
            if self.connected is False:
                raise Exception("Server failed to connect to IMAP server")
            
            self.logging.info("ECR connected")

            old_email_count = 0
            while(self.connected and not self.end_event.is_set()):
                server = self.server
                select_info = server.select_folder(ECR.MAILBOX)
                folder_status = server.folder_status(ECR.MAILBOX, 'UNSEEN')
                newmails = int(folder_status[b'UNSEEN'])
                if(old_email_count > newmails):#client has deleted some of their old mail, reset count
                    self.logging.info("emails being read detected")
                    old_email_count = 0
                elif(old_email_count == newmails):#no new emails to output
                    pass
                    #print("no new emails to output")
                else:
                    delta = newmails - old_email_count
                    messages = server.search('UNSEEN')
                    last_check = datetime.datetime.now()
                    email_list = []

                    # Extracting unread emails from IMAP Server 
                    self.extract_emails_from_IMAP(messages, email_list)

                    # filter msgs in email_list that aren't present in processed
                    filtered_emails = filter(self.is_not_processed, email_list)

                    # implicit filtering, only read delta emails
                    for i, msg_kv in enumerate(filtered_emails):
                        email_obj = ECR.extract_email(msg_kv)
                        email_subj = email_obj.get('Subject')
                        if type(email_subj) == list:
                            email_subj = " ".join(email_subj)
                        email_subj = email_subj.lower()
                        email_from = email_obj.get('From').lower()
                        email_body = None
                        email_multipart = []
                        if email_obj.is_multipart() :
                            for payload in email_obj.walk():
                                if payload.get_content_type() == 'text/plain':
                                    text = payload.get_payload().lower()
                                    email_multipart.append(text)
                        else:
                            email_body = email_obj.get_payload().lower()
                        email_tuple = (email_subj, email_from, email_body, email_multipart)
                        
                        self.put_email_in_queue(email_tuple)
                        self.processed_msgs.append(ECR.extract_msg_id(msg_kv))

                    # Marking extracted emails as unread
                    old_email_count = newmails
                time.sleep(self.check_freq)
                self.reconnect()
            
            self.shutdown()
            end_of_loop_str = "ECR:: end of email polling loop, connection=" + str(self.connected) + " endEvent=" + str(self.end_event.is_set())
            self.logging.info(end_of_loop_str)
        except KeyboardInterrupt:
            self.logging.info("ECR::closing email client")
            self.end_event.set()
            server.remove_flags(self.to_mark_unread, [SEEN])
            self.to_mark_unread = []
            server.logout()
            return
        except Exception as e:
            raise e
