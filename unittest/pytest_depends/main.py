from demo import test_foo,test_hi
from plugin import pytest_depend

@pytest_depend([test_foo,test_hi])
def test_bar():
    pass

@pytest_depend([test_foo,test_hi])
def test_bar2():
    pass
