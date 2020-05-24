import time
import re

class Rule:
    """ """
    def __init__(self, id, condition, audio):
        self.id = id
        self.condition = condition
        self.audio = audio

    def checkCondition(self)
    
    
class Condition:
    """ """
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

    def setTrue(self, word):
        if(word in self.terms):
            self.terms[word] = True

    def eval(self):
        eval_str = self.cond_str
        for key in self.terms.keys():
            eval_str = re.sub(r"\b%s\b" % key, str(self.terms[key]), eval_str)
            #eval_str = eval_str.replace(key,str(self.terms[key]))
        print(eval_str)
        return eval(eval_str)

