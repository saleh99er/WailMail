
"""" utility functions across all modules for Wail Mail"""

import queue

def get_from_queue(queue, end_event):
    while(not end_event.is_set()):
        try:
            el = queue.get(block=False)
            return el
        except:
            pass # try again
            


def put_in_queue(queue, element, end_event):
    while(not end_event.is_set()):
        try:
            queue.put(element, block=False)
            break
        except:
            pass # try again

def confirm_thread_finished(f):
    try:
        if(f.running() == True):
            return False
        x = f.result()
        return True
    except:
        return False