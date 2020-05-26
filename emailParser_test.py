from emailParser import *
from WailMail_common import *

import queue
import concurrent.futures
import logging
import threading
import time

# import emailClientReader
# import queue
# import concurrent
# import logging
# import threading
# import time


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

    condition_some_school = Condition("some_school.edu")
    result = condition_some_school.eval()
    assert(result == False)

    condition_some_school.set_true("some_school.edu")
    result = condition_some_school.eval()
    assert(result == True)

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
    logging.info("dummy e producer:: starting")
    email_bodies = ["your bill is due", "new assignment, have fun", "oh oops", "hey there, reminder to do X, Y, and Z"]
    while(not end_event.is_set()):
        time.sleep(1)
        email_tuple = ("somebody@some_school.edu", "Email #" + str(i), email_bodies[ i%4 ], [])
        put_in_queue(email_queue, email_tuple, end_event)
        logging.info("dummy e producer:: email #" +str(i) +" inserted")
        i += 1
    logging.info("dummy e producer:: exiting")

def dummy_producer_rules(rule_queue, end_event, logging):
    rules = []
    logging.info("dummy r producer:: starting")

    condition_some_school = Condition("somebody@some_school.edu")
    rule_yeet = Rule(0, condition_some_school, "screaming_sheep.mp3")
    rules.append(rule_yeet)

    condition_assignment = Condition("new and assignment")
    rule_uhoh = Rule(1, condition_assignment, "siren.mp3")
    rules.append(rule_uhoh)


    rule_count = 0

    logging.info("dummy r producer:: done setting up initial rules")
    while(not end_event.is_set() and rule_count < len(rules)):
        logging.info("dummy r producer:: iteration")
        time.sleep(5)
        put_in_queue(rule_queue, rules[rule_count], end_event)
        logging.info("dummy r producer:: rule #" +str(rule_count) +" inserted")
        rule_count += 1

    logging.info("dummy r producer:: exiting")

def dummy_consumer_audio(audio_queue, end_event, logging):
    logging.info("dummy a consumer:: starting")
    while(not end_event.is_set()):
        time.sleep(1)
        if(not audio_queue.empty()):
            audio_request = get_from_queue(audio_queue, end_event)
            if(audio_request is not None):
                logging.info("dummy a consumer::" + audio_request)
    logging.info("dummy a consumer:: exiting")

def email_parser_util_tests():
    email_1_tuple = ("somebody@some_school.edu", "Email #1", "hello world", [])
    condition_some_school = Condition("somebody@some_school.edu")
    rule_yeet = Rule(0, condition_some_school, "screaming_sheep.mp3")
    result = EmailParser.check_email_for_rule(rule_yeet, email_1_tuple)
    assert result == True

    condition_some_school = Condition("some_school.edu")
    result = EmailParser.check_email_for_rule(rule_yeet, email_1_tuple)
    assert result == True

    print("all Email Parser util function tests pass")


        

def emailparser_tests(test_duration):

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.basicConfig(format=format, level=logging.WARN,
                        datefmt="%H:%M:%S")
    logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.INFO)

    end_event = threading.Event()
    email_queue = queue.Queue()
    rule_queue = queue.Queue()
    audio_queue = queue.Queue()
    ep = EmailParser(email_queue, rule_queue, audio_queue, end_event, logging)
    seconds = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        email_producer_future = executor.submit(dummy_producer_email, email_queue, end_event, logging)
        rule_producer_future = executor.submit(dummy_producer_rules, rule_queue, end_event, logging)
        ep_consumer_future = executor.submit(ep.parseQueues)
        audio_consumer_future = executor.submit(dummy_consumer_audio, audio_queue, end_event, logging)

        while(seconds < test_duration):
            logging.info("t=" +str(seconds))
            logging.info("EPF::" + str(email_producer_future))
            logging.info("RPF::" + str(rule_producer_future))
            logging.info("EPCF::" + str(ep_consumer_future))
            logging.info("ACF::" + str(audio_consumer_future))

            time.sleep(1)
            seconds += 1
        
        end_event.set()
        time.sleep(10)
        logging.info("EPF::" + str(email_producer_future))
        assert confirm_thread_finished(email_producer_future)
        logging.info("RPF::" + str(rule_producer_future))
        assert confirm_thread_finished(rule_producer_future)
        logging.info("EPCF::" + str(ep_consumer_future))
        assert confirm_thread_finished(ep_consumer_future)
        logging.info("ACF::" + str(audio_consumer_future))
        assert confirm_thread_finished(audio_consumer_future)
        print("Email Parser class tests passed")

    print(end_event.is_set())

    

condition_tests()
rule_tests()
email_parser_util_tests()
emailparser_tests(20)
