import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestAsQbservable(unittest.TestCase):

    def test_select(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(200, 2), on_next(500, 3), on_next(600, 4))
        results = scheduler.create_observer()

        def create():
            return xs.as_qbservable().select("lambda x: x*10")

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(500, 30), on_next(600, 40))

    def test_select_select(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(200, 2), on_next(500, 3), on_next(600, 4))
        results = scheduler.create_observer()

        def create():
            return xs.as_qbservable().select("lambda x: x*10").select("lambda x: x+1")

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(500, 31), on_next(600, 41))


if __name__ == '__main__':
    unittest.main()
