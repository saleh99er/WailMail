import emailClientReader
import queue
import concurrent
import logging
import threading
import time

def consumer(queue, logging, endEvent):
    try:
        logging.info("starting consumer")
        while(not endEvent.is_set()):
            queue_el = queue.get()
            logging.info(queue_el[0])
    except KeyboardInterrupt:
        queue.get()
        logging.info("Consumer:: Keyboard interrupt, exiting")
        endEvent.set()

endEvent = threading.Event()
emailQueue = queue.Queue()
ctrlQueue = queue.Queue()
ecr = emailClientReader.ECR(emailQueue, endEvent, logging)
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
        logging.info("started producer")
        consumer_future = executor.submit(consumer, (emailQueue, logging, endEvent))
        logging.info("started consumer")
        while(True):
            time.sleep(1)
            logging.info("q size " + str(emailQueue.qsize()))
            logging.info(producer_future)
            #producer_future.result()
            logging.info(consumer_future)
            #consumer_future.result()
