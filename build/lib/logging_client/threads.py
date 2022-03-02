import threading

from .consumer import ReconnectingConsumer
from .publisher import Publisher

print_lock = threading.Lock()


class PrimaryThread(threading.Thread):
    def __init__(self, queue, amqp_url, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.publisher = Publisher(amqp_url)
        self.daemon = True
        self.stop_threads = False
        self._return = None
        self.start()

        self.consumer = ReconnectingConsumer(amqp_url)
        self.thread_2 = threading.Thread(target=self.consumer.run)
        self.thread_2.setDaemon(True)
        self.thread_2.start()

    def run(self):
        print(threading.currentThread().getName(), self.stop_threads, "primary")
        while True:
            if self.stop_threads:
                self.consumer.prepare_stop_consumer()
                while self.consumer.is_stopped_consumer() is False:
                    import time

                    time.sleep(1)
                    print("preparing consumer stop...")
                    is_stopped = self.consumer.is_stopped_consumer()
                    print(f"is_stopped: {is_stopped}")
                self.consumer.stop()
                print("killed")
                break
            else:
                while not self.queue.empty():
                    val = self.queue.get()
                    self._return = self.logmsg_publish(val)

    def logmsg_publish(self, logmsg):
        with print_lock:
            print(
                threading.currentThread().getName(),
                "Publisher: Received {}".format(logmsg),
            )
            self.publisher.run(logmsg)

    def kill(self):
        self.stop_threads = True

    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return
