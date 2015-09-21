from rx import Observable


def main():
    xs = Observable.from_([1, 2, 3]).as_qbservable()
    ys = xs.select("lambda x: x+1")
    print(ys)
    print("subscribing")
    subscription = ys.subscribe(print)
    subscription.dispose()

if __name__ == '__main__':
    main()
