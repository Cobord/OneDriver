"""
a class which contains an iterator
we have a method on it which combines 2 such instances
    into self
we would only want one source driving the other iterator to completion
    to be the part that is in self
but in this manner without the features of this package that
    we don't get errors
    but instead just wrong behavior
"""
#pylint:disable=R0801

from __future__ import annotations
from itertools import chain
from typing import List, Optional

class ContainsIterator:
    """
    contains a private iterator
    """
    def __init__(self, initial_vals: List[int]):
        self.__f = iter(initial_vals)

    def combine(self, other : ContainsIterator):
        """
        self then other
        """
        #pylint:disable=protected-access
        self.__f = chain(self.__f, other.__f)

    def consume_to_list(self) -> List[int]:
        """
        entire iterator consumed, left empty
        """
        return_val = iter([])
        self.__f, return_val = return_val, list(self.__f)
        return return_val

    def consume_one(self) -> Optional[int]:
        """
        one piece of iterator consumed
        """
        return next(self.__f, None)


def test_2_objects():
    """
    what happens when have two places driving iteration
    """
    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    x.combine(y)
    assert y.consume_to_list() == [4,5,6]
    assert x.consume_to_list() == [1,2,3]

    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    x.combine(y)
    assert x.consume_to_list() == [1,2,3,4,5,6]
    assert not y.consume_to_list()

    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    x.combine(y)
    assert y.consume_one() == 4
    assert x.consume_to_list() == [1,2,3,5,6]
    assert not y.consume_to_list()

    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    x.combine(y)
    assert y.consume_one() == 4
    assert y.consume_to_list() == [5,6]
    assert x.consume_to_list() == [1,2,3]

def test_one_object():
    """
    what happens when have combining with self
    """
    x = ContainsIterator([1,2,3])
    x.combine(x)
    assert x.consume_to_list() == [1,2,3]
