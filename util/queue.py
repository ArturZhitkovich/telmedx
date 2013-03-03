#################################################################################
# @file queue.py
# @brief  discarding queue
# @author 
# Creation Date  
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Author          Description
#    
#################################################################################
"""discarding queue wrapper - both methods will drop an element from the queue if it is full"""
import gevent.queue

class DiscardingQueue(gevent.queue.Queue):
    def put(self, item, **kwargs):
        if self.full():
            self.get()
            
        super(DiscardingQueue, self).put(item, **kwargs)
        
    def put_nowait(self, item):
        if self.full():
            self.get()
            
        super(DiscardingQueue, self).put_nowait(item)
        