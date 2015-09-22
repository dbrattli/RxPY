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

    def test_as_qbservable_(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(200, 2), on_next(500, 3), on_next(600, 4))
        results = scheduler.create_observer()

       	def create():
        	return xs.as_qbservable()

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(500, 3), on_next(600, 4))

if __name__ == '__main__':
    unittest.main()
