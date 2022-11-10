#


class Observable():
    def __init__(self):
        self.observers = []

    def register_observer(self, observer):
        if (observer in self.observers):
            return
        self.observers.append(observer)

    def unregister_observer(self, observer):
        if (observer not in self.observers):
            return
        self.observers.pop(self.observers.index(observer))

class SiObserver():
    def on_section(self, si_collector, result, section, sub_table, table):
        pass

    def on_warning(self, si_collector, section, string):
        pass

class EitObserver():
    def on_eit_section(self, eit_collector, result, section,
                       sub_table, svc_table, table):
        pass

    def on_eit_warning(self, eit_collector, section, string):
        pass

class SvcObserver():
    def update(self, svc_list, services, cur_service):
        pass

class LogObserver():
    def on_log(self, logger, string):
        pass

class FeObservable():
    def __init__(self):
        self.observers = []

    def register_observer(self, observer):
        if (observer in self.observers):
            return
        self.observers.append(observer)

    def unregister_observer(self, observer):
        if (observer not in self.observers):
            return
        self.observers.pop(self.observers.index(observer))

    def notify_observers(self, event):
        for observer in self.observers:
            observer.update(self, event)

class FeObserver():
    def update(self, fe, event):
        pass

    def vote_against_tuning(self, fe, param):
        "returns its level if it is against"
        return 0

