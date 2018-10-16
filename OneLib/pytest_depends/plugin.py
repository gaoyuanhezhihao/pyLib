import functools
import pytest

def check_depends(depends):
    try:
        for dep in depends:
            dep()
    except Exception as e:
        return dep
    else:
        return True

def pytest_depend(depends):
    def pytest_depend_decorator(func):
        stat = check_depends(depends)
        if stat is True:
            return func
        else:
            return pytest.mark.skip(True, reason="%s[skip] --> %s[Failed]" % (func.__name__, stat.__name__))(func)
    return pytest_depend_decorator


