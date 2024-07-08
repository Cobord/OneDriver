"""
a class which contains a closure
we have a method on it which combines 2 such instances
    into self
but we only want one source calling the closure
    to be the part that is in self
using the features of this package that
    so that we do get the appropriate errors
"""
#pylint:disable=R0801

from __future__ import annotations

from ..one_driving.workaround import ConsumedObjectError, handle_args_repeats, invalidate_these_args

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
        self.__invalid = False

    def clone(self):
        """
        a clone which can be independently driven
        """
        cur_counter = self.__counter
        to_return = ContainsClosure()
        #pylint:disable=protected-access,unused-private-member
        to_return.__counter = cur_counter
        return to_return

    def invalidate(self):
        """
        mark that it shouldn't be used anymore
        """
        self.__invalid = True

    def is_valid(self):
        """
        query if can have an independent reference to this object
        """
        return not self.__invalid

    #pylint:disable=no-value-for-parameter
    @handle_args_repeats(cloner=lambda obj: obj.clone())
    @invalidate_these_args(invalidating_locs=(True,[1]),do_invalidate=lambda obj: obj.invalidate(),
                           validation_query=lambda obj: obj.is_valid())
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

    def consume_one(self, ignore_validity: bool = False) -> int:
        """
        one call to the closure
        """
        if self.__invalid and not ignore_validity:
            raise ConsumedObjectError
        return self.__f()

def test_2_objects():
    """
    what happens when have two places calling closure
    """
    x = ContainsClosure()
    y = ContainsClosure()
    x.combine(y)
    assert y.consume_one(True) == 1
    assert y.consume_one(True) == 2
    assert y.consume_one(True) == 3
    assert not y.is_valid()
    errored = False
    try:
        assert y.consume_one() == 4
    except ConsumedObjectError:
        errored = True
    assert errored
    # y's count is 4 which gets added to x's 1
    assert x.consume_one() == 5

    x = ContainsClosure()
    y = ContainsClosure()
    x.combine(y)
    # x's count is 1 plus y's 1
    assert x.consume_one() == 2
    # y's count was 1 before because x called the closure in previous line
    # now it is 2
    assert y.consume_one(True) == 2
    assert y.consume_one(True) == 3
    assert y.consume_one(True) == 4
    assert not y.is_valid()
    errored = False
    try:
        assert y.consume_one() == 5
    except ConsumedObjectError:
        errored = True
    assert errored
    # x's count is 2 plus y's 5
    assert x.consume_one() == 7

def test_one_object():
    """
    what happens when have combining with self
    """
    x = ContainsClosure()
    x.combine(x)
    #pylint:disable=import-outside-toplevel
    assert x.consume_one() == 2
