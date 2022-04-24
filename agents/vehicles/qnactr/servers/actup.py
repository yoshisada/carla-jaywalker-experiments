from pyactup import Memory


def test_pyactup():
    print('test_pyactup')
    m = Memory()
    print(m.learn(color="red", size=4))
    print(m.time)
    print(m.learn(color="blue", size=4))
    print(m.time)
    print(m.learn(color="red", size=3))
    print(m.time)
    c = m.retrieve(color="red")
    print(c)
    print(m.time)
    pass


def test_pyactup_2():
    print('test_pyactup_2')
    m = Memory()
    m.learn(color="red", utility=1)
    m.learn(color="blue", utility=2)
    m.learn(color="red", utility=1.8)
    m.learn(color="blue", utility=0.9)
    m.best_blend("utility", ({"color": c} for c in ("red", "blue")))
    m.learn(color="blue", utility=-1)
    m.best_blend("utility", ("red", "blue"), "color")
    pass



if __name__ == '__main__':
    test_pyactup_2()