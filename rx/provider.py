from . import Qbservable


class Provider(object):
    def __init__(self):
        pass

    def create_query(self, expression):
        def subscribe(observer):
            raise NotImplemented

        return Qbservable(subscribe, self, expression)

    def execute(self, expression):
        raise NotImplemented
