import time
import re
from WailMail_common import *

import logging
import threading
import queue

class Rule:
    """ """
    def __init__(self, id, condition, audio):
        self.id = id
        self.condition = condition
        self.audio = audio

    def check_condition(self):
        return self.condition.eval()
    
    def terms_of_interest(self):
        return list(self.condition.terms.keys())
    
    def set_true_term(self, word):
        self.condition.set_true(word)

    def reset_state(self):
        self.condition.reset_state()
    
    
class Condition:
    """ 
    class to represent email conditional expressions, 
    a word represents a term and is true if it occurs at
    least once in from, subject, or email body
    """
    do_not_replace = ['not', 'and', 'or', '(', ')']

    def neq(s, check_these):
        for check in check_these:
            if(s == check):
                return False
        return True

    def adjust_paren(str_list):
        i = 0
        while(i < len(str_list)):
            s = str_list[i]
            open_paren_index = s.find("(")
            close_paren_index = s.find(")")
            if(open_paren_index > -1):
                term = s[open_paren_index+1:]
                str_list[i] = "("
                str_list.insert(i+1, term)
            elif(close_paren_index > 0):
                term = s[:close_paren_index]
                str_list[i] = term
                str_list.insert(i+1, ")")
            i += 1
        
    def __init__(self, cond_str):
        self.terms = {} # string key, boolean val dictionary
        self.str_list = cond_str.split()
        Condition.adjust_paren(self.str_list)
        self.cond_str = " ".join(self.str_list)
        for word in self.str_list:
            if(Condition.neq(word, Condition.do_not_replace)):
                self.terms[word] = False

    def set_true(self, word):
        if(word in self.terms):
            self.terms[word] = True

    def reset_state(self):
        for word in self.terms:
            self.terms[word] = False

    def eval(self):
        eval_str = self.cond_str
        for key in self.terms.keys():
            eval_str = re.sub(r"\b%s\b" % key, str(self.terms[key]), eval_str)
        #print(eval_str)
        return eval(eval_str)

class EmailParser:

    def __init__(self, email_queue, rule_queue, audio_queue, end_event, logging, check_freq=5):
        self.email_queue = email_queue
        self.rule_queue = rule_queue
        self.audio_queue = audio_queue
        self.end_event = end_event
        self.rules = {}
        self.logging = logging
        self.check_freq = check_freq

    def check_email_for_rule(rule, email_tuple):
        """
        Returns True if rule terms evaluate to true for the term occurences
        present in email_tuple, False Otherwise.
        """
        rule.reset_state()
        terms_to_check = rule.terms_of_interest()

        for i in range(0, 3):
            if(email_tuple[i] != None and type(email_tuple[i]) == str):
                for term in terms_to_check:
                    if(re.search(r'\b' + term + r'\b', email_tuple[i])):
                        rule.set_true_term(term)
        for part in email_tuple[3]:
            if(part != None and type(part) == str):
                if(re.search(r'\b' + term + r'\b', part)):
                        rule.set_true_term(term)
        return rule.check_condition()

    
    def parseQueues(self):
        self.logging.info("EP:: start of parsing queues")
        while(not self.end_event.is_set()):
            # add new rules as they're received from the rule_queue
            if(not self.rule_queue.empty()):
                rule = get_from_queue(self.rule_queue, self.end_event)
                self.rules[rule.id] = rule
                self.logging.info("EP:: added rule " + str(rule.id))

            check_rules = list(self.rules.values())
            

            # extract emails from email queue until empty, check all rules for each email from queue
            while(not self.email_queue.empty()):
                email_tuple = get_from_queue(self.email_queue, self.end_event)
                self.logging.info("EP:: got email " + str(email_tuple[0]))
                
                for rule in check_rules:
                    email_passes_rule = EmailParser.check_email_for_rule(rule, email_tuple)
                    # self.logging.info("cefr helper:" +str(email_passes_rule))
                    if(email_passes_rule):
                        self.logging.info("EP:: rule event occurred, scheduling " + rule.audio)
                        put_in_queue(self.audio_queue, rule.audio, self.end_event)
            time.sleep(self.check_freq)
        self.logging.info("EP:: end of parsing queues")

                


            
            

