import select
import sys
import errno
import time
import copy

POLLIN = select.POLLIN
POLLOUT = select.POLLOUT
POLLERR = select.POLLERR

class PollLoop:
    class __impl:
        """ Implementation of the singleton interface """

        def __init__(self):
            self.pollfds = select.poll()
            self.stopped = False
            self.callbacks = {}
            self.timers = []
            self.cur_time = time.time()
            self.current_timer = None
            self.timer_changed = False
            self.resizer = None

        def register_resizer(self, resizer):
            self.resizer = resizer

        def register(self, fd, mode, callback, *args, **kwargs):
            self.pollfds.register(fd, mode)
            self.callbacks[fd] = (callback, args, kwargs)
            return fd

        def unregister(self, fd):
            if (self.callbacks.get(fd)):
                self.pollfds.unregister(fd)
                callback, args, kwargs = self.callbacks.pop(fd)
                del callback, args, kwargs

        def register_timer(self, callback, after_msec, interval_msec,
                           *args, **kwargs):
            if (after_msec <= 0):
                return
            next_expire = time.time() + after_msec / 1000
            new_timer = (callback, next_expire, interval_msec, args, kwargs)
            for i in range(0, len(self.timers)):
                timer = self.timers[i]
                if (timer is None):
                    continue
                if (callback == timer[0]):
                    self.timers[i] = new_timer
                    if (callback == self.current_timer):
                        self.timer_changed = True
                    return
            self.timers.append(new_timer)

        def unregister_timer(self, callback):
            for i in range(0, len(self.timers)):
                timer = self.timers[i]
                if (timer is None):
                    continue
                if (callback == timer[0]):
                    self.timers.pop(i)
                    if (callback == self.current_timer):
                        self.timer_changed = True
                    return

        def run_timer(self):
            cur_time = time.time()
            run = True
            while (run):
                run = False
                for i in range(0, len(self.timers)):
                    timer = self.timers[i]
                    callback, next_expire, interval_msec, args, kwargs = timer
                    if (next_expire <= cur_time):
                        self.timer_changed = False
                        self.current_timer = callback
                        callback(*args, **kwargs)
                        self.current_timer = None
                        run = True
                        if (self.timer_changed == False):
                            if (interval_msec):
                                self.timers[i] = timer
                                cur_time = time.time()
                                next_expire = cur_time + interval_msec / 1000
                                timer = (callback, next_expire, interval_msec,
                                         args, kwargs)
                                self.timers[i] = timer
                            else:
                                self.timers.pop(i)
                        break

        def run(self):
            while (self.stopped == False):
                try:
                    ready = self.pollfds.poll(100)
                    if (len(ready) != 0):
                        # process only the first one
                        fd, mode = ready[0]
                        callback, args, kwargs = self.callbacks.get(fd)
                        if (callback):
                            callback(fd, mode, *args, **kwargs)

                    self.run_timer()
                except select.error:
                    if (self.resizer):
                        self.resizer()
                    continue

        def stop(self):
            self.stopped = True

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if PollLoop.__instance is None:
            # Create and remember instance
            PollLoop.__instance = PollLoop.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_PollLoop__instance'] = PollLoop.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr)

if __name__ == "__main__":
    class TestIt:
        def __init__(self):
            self.seq = 0
            self.poller = PollLoop()
            self.poller.register_timer(self.timer_callback1, 2000, 1000)

        def timer_callback1(self):
            c = time.time()
            print("1 -- %d: %f" % (self.seq, c))
            self.seq += 1
            if (self.seq == 2):
                print("change self")
                self.poller.register_timer(self.timer_callback1, 2000, 2000)
            elif (self.seq == 4):
                print("add other")
                self.poller.register_timer(self.timer_callback2, 1000, 2000,
                                           10)
            elif (self.seq == 6):
                print("remove self")
                self.poller.unregister_timer(self.timer_callback1)

        def timer_callback2(self, arg):
            c = time.time()
            print("2 -- %d: %f" % (self.seq, c))
            self.seq += 1
            if (self.seq == 8):
                print("remove self")
                self.poller.unregister_timer(self.timer_callback2)

    tester = TestIt()
    tester.poller.run()

