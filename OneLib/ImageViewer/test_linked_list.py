from linked_list import LinkedList

def test_linked_list0():
    LL = LinkedList()
    for i in range(10):
        LL.push_back(i)
    assert list(LL) == list(range(10))


def test_linked_list():
    LL = LinkedList()
    for i in range(10):
        LL.push_back(i)

    for i in range(1, 10):
        LL.erase(LL.head())
        assert LL.head().data == i
        assert not LL.empty()
    LL.erase(LL.head())
    assert LL.empty()

def test_linked_list2():
    LL = LinkedList()
    for i in range(3):
        LL.push_back(i)
    last = LL.push_back(20)
    LL.erase(last)
    LL.push_back(30)
    assert list(LL) == [0, 1, 2, 30]

def test_reset_linked_list():
    LL = LinkedList()
    a = LL.push_back(0)
    b = LL.push_back(1)
    c = LL.push_back(2)
    LL.erase(a)
    LL.erase(b)
    LL.erase(c)
    a = LL.push_back(0)
    b = LL.push_back(1)
    c = LL.push_back(2)
    assert list(LL) == [0, 1, 2]

def test_reset_linked_list2():
    LL = LinkedList()
    a = LL.push_back(0)
    b = LL.push_back(1)
    c = LL.push_back(2)
    LL.erase(c)
    LL.erase(b)
    LL.erase(a)
    a = LL.push_back(0)
    b = LL.push_back(1)
    c = LL.push_back(2)
    assert list(LL) == [0, 1, 2]
