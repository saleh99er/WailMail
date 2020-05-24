from emailParser import *
from WailMail_common import *

def condition_tests():
    condition_grades = Condition("(cms or gradescope) or piazza or some_school.edu")
    result = condition_grades.eval()
    assert(result == False)
    
    condition_grades.set_true("fake")
    result = condition_grades.eval()
    assert(result == False)

    condition_grades.set_true("gradescope")
    result = condition_grades.eval()
    assert(result == True)

    condition_grades.set_true("some_school.edu")
    result = condition_grades.eval()
    assert(result == True)

    condition_grades.reset_state()
    result = condition_grades.eval()
    assert(result == False)
    
    condition_workday = Condition("workday and not (timestamp and due)")
    result = condition_workday.eval()
    assert(result == False)

    condition_workday.set_true("workday")
    result = condition_workday.eval()
    assert(result == True)

    condition_workday.set_true("timestamp")
    result = condition_workday.eval()
    assert(result == True)

    condition_workday.set_true("due")
    result = condition_workday.eval()
    assert(result == False)

    condition_campus = Condition("not north and not northcampus")
    result = condition_campus.eval()
    assert(result == True)

    condition_campus.set_true("north")
    result = condition_campus.eval()
    assert(result == False)

    print("Condition class tests passed")

def rule_tests():
    condition_grades = Condition("(cms or gradescope) or piazza or some_school.edu")
    rule_yeet = Rule(1, condition_grades, "yeet.mp3")
    
    result = rule_yeet.check_condition()
    assert(result == False)

    rule_yeet.set_true_term("some_school.edu")
    result = rule_yeet.check_condition()
    assert(result == True)

    terms = rule_yeet.terms_of_interest()
    assert(terms == ["cms", "gradescope", "piazza", "some_school.edu"])
    
    print("Rule class tests passed")

def dummy_producer_email(email_queue, end_event, logging):
    i = 0
    email_bodies = ["your bill is due", "new assignment, have fun", "oh oops", "hey there, reminder to do X, Y, and Z"]
    while(not endEvent.is_set()):
        time.sleep(1)
        email_tuple = ("somebody@some_school.edu", "Email #" + str(i), email_bodies[ i%4 ], [])
        put_in_queue(email_queue, email_tuple, end_event)
        logging.info("dummy e producer:: email #" +str(i) +" inserted")
        i += 1
    logging.info("dummy e producer:: exiting")


def dummy_producer_rules(rule_queue, end_event, logging):
    rules = []

    condition_some_school = Condition("some_school.edu")
    rule_yeet = Condition(0, condition_some_school, "screaming_sheep.mp3")
    rules.append(rule_yeet)

    while(not endEvent.is_set() and i < len(rules)):
        time.sleep(10)
        put_in_queue(rule_queue, email_tuple, end_event)
        logging.info("dummy r producer:: rule #" +str(i) +" inserted")
    logging.info("dummy r producer:: exiting")


def emailparser_tests():
    pass # TO DO
    

condition_tests()
rule_tests()