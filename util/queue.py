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
