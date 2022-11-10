import dvb
import logging
import observer
import db_center


class SvcList(observer.Observable):
    def __init__(self):
        self.db = db_center.DbCenter()
        self.connection = self.db.connection
        self.services = []
        self.cur_service = None
        self.top_service = None
        self.height = 0
        self.logger = logging.getLogger('MainLog')
        observer.Observable.__init__(self)
        self.order_str = [
            'sources.src_key, nid, lcn, type, onid, tsid, svid',
            'sources.src_key, lcn, type, nid, onid, tsid, svid',
            'sources.src_key, transports.ts_key, lcn, type, nid, onid, tsid, svid',
            'services.svc_name, sources.src_key, onid, tsid, svid',
        ]
        self.order_by = 0

    def set_window_height(self, height):
        self.height = height

    def read_services(self):
        if (self.top_service and self.cur_service):
            top_index = self.services.index(self.top_service)
            cur_index = self.services.index(self.cur_service)
            top_offset = cur_index - top_index
        else:
            top_offset = 0

        self.services = []
        c = self.connection.cursor()

        query = '''select services.svc_key, services.svc_name, prov_name, type,
                tsid, onid, nid, svid, services.ts_key,
                sources.src_key, delivery_system, lcn
                from (services join transports
                          on services.ts_key = transports.ts_key)
                      join sources
                          on transports.src_key = sources.src_key
                      left outer join lcn
                          on services.svc_key = lcn.svc_key
                order by '''
        query += self.order_str[self.order_by]
        c.execute(query)
        rows = c.fetchall()

        string = self.order_str[self.order_by]
        self.logger.info("order by [" + str(self.order_by) + "] " + string)

        if (not rows):
            self.cur_service = None
            self.top_service = None
            return 0

        for row in rows:
            service = dvb.Service(row['svc_key'], row['lcn'],
                                  row['svc_name'], row['prov_name'],
                                  row['type'],
                                  row['tsid'], row['onid'], row['svid'],
                                  row['ts_key'],
                                  row['src_key'], row['delivery_system'])
            self.services.append(service)

        if (self.cur_service):
            for service in self.services:
                if (self.cur_service.svc_key == service.svc_key):
                    self.cur_service = service
                    break
        if (self.cur_service in self.services):
            cur_index = self.services.index(self.cur_service)
            top_index = cur_index - top_offset
            if (top_index < 0):
                top_index = 0
            self.top_service = self.services[top_index]
        else:
            self.cur_service = self.services[0]
            self.top_service = self.services[0]
        #self.logger.debug("read %d services" % len(self.services))

    def get_services_in_window(self):
        if (len(self.services) == 0 or self.cur_service is None):
            return []
        top_index = self.services.index(self.top_service)
        to = len(self.services)
        if (top_index + self.height < to):
            to = top_index + self.height

        return self.services[top_index:to]

    def notify_observers(self):
        service_list = self.get_services_in_window()
        for observer in self.observers:
            observer.update(self, service_list, self.cur_service)

    def get_cur_service(self):
        return self.cur_service

    def move_up(self):
        if (len(self.services) == 0 or self.cur_service is None):
            return
        cur_index = self.services.index(self.cur_service)
        if (cur_index <= 0):
            return
        cur_index -= 1
        self.cur_service = self.services[cur_index]

        top_index = self.services.index(self.top_service)
        if (top_index > cur_index):
            self.top_service = self.cur_service
        self.notify_observers()

    def move_down(self):
        if (len(self.services) == 0 or self.cur_service is None):
            return
        cur_index = self.services.index(self.cur_service)
        if (cur_index >= len(self.services) - 1):
            return
        cur_index += 1
        self.cur_service = self.services[cur_index]

        top_index = self.services.index(self.top_service)
        last_scr_service = self.height + top_index
        if (last_scr_service <= cur_index):
            top_index += 1
            self.top_service = self.services[top_index]
        self.notify_observers()

    def order_plus(self):
        self.order_by += 1
        self.order_by %= len(self.order_str)
        self.read_services()
        self.notify_observers()

    def order_minus(self):
        self.order_by -= 1
        self.order_by %= len(self.order_str)
        self.read_services()
        self.notify_observers()

