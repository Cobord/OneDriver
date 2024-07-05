"""
a class which contains a closure
we have a method on it which combines 2 such instances
    into self
but we only want one source calling the closure
    to be the part that is in self
but in this manner without the features of this package that
    we don't get errors
    but instead just wrong behavior
"""
from __future__ import annotations

class ContainsClosure:
    """
    contains a private iterator
    """
    def __init__(self):
        self.__counter = 0
        def f():
            self.__counter += 1
            return self.__counter
        self.__f = f

    def combine(self, other : ContainsClosure):
        """
        self + other
        """
        #pylint:disable=protected-access,unnecessary-lambda-assignment
        old_self_f = lambda: 0
        old_self_f, self.__f = self.__f, old_self_f
        def combined() -> int:
            from_self = old_self_f()
            from_other = other.__f()
            return from_self + from_other
        self.__f = combined

    def consume_one(self) -> int:
        """
        one call to the closure
        """
        return self.__f()

def test_2_objects():
    """
    what happens when have two places driving iteration
    """
    x = ContainsClosure()
    y = ContainsClosure()
    x.combine(y)
    assert y.consume_one() == 1
    assert y.consume_one() == 2
    assert y.consume_one() == 3
    # y's count is 4 which gets added to x's 1
    assert x.consume_one() == 5

    x = ContainsClosure()
    y = ContainsClosure()
    x.combine(y)
    # x's count is 1 plus y's 1
    assert x.consume_one() == 2
    # y's count was 1 before because x called the closure in previous line
    # now it is 2
    assert y.consume_one() == 2
    assert y.consume_one() == 3
    assert y.consume_one() == 4
    # x's count is 2 plus y's 5
    assert x.consume_one() == 7
