import emailClientReader
import queue
import concurrent
import logging
import threading
import time

def get_email_in_queue(email_queue, endEvent):
    while(not endEvent.is_set()):
        try:
            queue_el = email_queue.get(block=False)
            logging.info("got email from queue")
            return queue_el
        except queue.Empty:
            pass
    return None

def consumer(queue, logging, endEvent):
    try:
        logging.info("starting consumer")
        while(not endEvent.is_set()):
            queue_el = get_email_in_queue(queue, endEvent)
            if(queue_el is None):
                logging.info("Consumer:: End event set")
                return
            logging.info(queue_el[0])
        logging.info("Consumer:: End event set")
    except KeyboardInterrupt:
        logging.info("Consumer:: Keyboard interrupt, exiting")
        queue.get()
        endEvent.set()

endEvent = threading.Event()
emailQueue = queue.Queue()
ctrlQueue = queue.Queue()
ecr = emailClientReader.ECR(emailQueue, endEvent, logging, check_freq=5)
print(endEvent.is_set())

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")
logging.basicConfig(format=format, level=logging.WARN,
                    datefmt="%H:%M:%S")
logging.basicConfig(format=format, level=logging.DEBUG,
                    datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.INFO)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        producer_future = executor.submit(ecr.startECR)
        logging.info("ECR_test::started producer")
        consumer_future = executor.submit(consumer, emailQueue, logging, endEvent)
        logging.info("ECR_test::started consumer")

        i = 0
        try:
            while(i < 10):
                time.sleep(1)
                logging.info("ECR_test:: q size " + str(emailQueue.qsize()))
                logging.info(producer_future)
                #producer_future.result()
                logging.info(consumer_future)
                i += 1
                #consumer_future.result()
            endEvent.set()
            logging.info("ECR_test:: set end event")
            time.sleep(10)
            logging.info(producer_future)
            logging.info(consumer_future)

        except Exception as e:
            logging.info("ECR_test:: exception occurred")
            logging.info(e)
            

