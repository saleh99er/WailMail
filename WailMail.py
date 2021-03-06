#!/usr/bin/python3

from flask import Flask, request, render_template

from emailClientReader import *
from emailParser import *
from audio_player import audio_player
from WailMail_common import *
import queue
import threading
import logging
import time



def flask_app(rule_queue, end_event):
    # key := id, value := rule
    rules = {} 
    app = Flask(__name__)

    def determineUnusedId():
        for i in range(1000):
            if(not i in rules):
                return i

    @app.route('/')
    def index():
        rules_so_far = [str(rule) for rule in list(rules.values())]
        return render_template('index.html', rules_so_far = rules_so_far, rule_suggestion = "0: github or bug -> screaming_sheep.mp3")

    @app.route('/submit', methods=['POST'])
    def submit():
        rule_str = request.form['new_rule']
        rule = Rule.str_to_rule(rule_str)
        if(rule is not None):
            rules[rule.id] = rule
            put_in_queue(rule_queue, rule, end_event)

            rules_so_far = [str(rule) for rule in list(rules.values())]
            suggestion = str(determineUnusedId()) + ": woah or dude -> john_cena.mp3"
            return render_template('index.html', rules_so_far = rules_so_far, rule_suggestion=suggestion)

    @app.route('/shutdown', methods=['GET'])
    def shutdown():
        end_event.set()
        return "Thanks for using Wail Mail, bye bye"

    app.run(host='0.0.0.0')

   



if __name__ == '__main__':

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

    ecr = ECR(email_queue, end_event, logging, 15)
    ep = EmailParser(email_queue, rule_queue, audio_queue, end_event, logging)

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        flask_thread = threading.Thread(name="Flask thread", target=flask_app, args=(rule_queue, end_event), daemon=True)
        flask_thread.start()
        ecr_future = executor.submit(ecr.startECR)
        ep_future = executor.submit(ep.parseQueues)
        ap_future = executor.submit(audio_player, audio_queue, end_event, logging)
    
        futures = [ecr_future, ep_future, ap_future]
        seconds = 0

        logging.info("Main::all threads started")

        while(not end_event.is_set()):
            for number, future in enumerate(futures):
                logging.info(str(number) + ":" + str(future))
            time.sleep(5)
            seconds += 5

        time.sleep(1)
        

