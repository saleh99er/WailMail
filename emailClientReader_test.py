import emailClientReader
import queue

def consumer():
    pass # to implement to confirm ECR thread

queue = queue.Queue()
ecr = emailClientReader.ECR(queue)
ecr.startECR()