"""
a class which contains an iterator
we have a method on it which combines 2 such instances
    into self
but we only want one source driving the other iterator to completion
    to be the part that is in self
"""
#pylint:disable=R0801

from __future__ import annotations
from itertools import chain
from typing import List, Optional

from ..one_driving.workaround import ConsumedObjectError, SameObjectError, \
    handle_args_repeats, invalidate_these_args

class ContainsIterator:
    """
    contains a private iterator
    combine/combine_many does not automatically clone, but does checks validity and invalidates
    """
    def __init__(self, initial_vals: List[int]):
        self.__f = iter(initial_vals)
        self.__invalid = False

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
    @handle_args_repeats(cloner=None)
    @invalidate_these_args(invalidating_locs=(True,[1]),do_invalidate=lambda obj: obj.invalidate(),
                           validation_query=lambda obj: obj.is_valid())
    def combine(self, other : ContainsIterator):
        """
        self then other
        """
        #pylint:disable=protected-access
        self.__f = chain(self.__f, other.__f)

    #pylint:disable=no-value-for-parameter
    @handle_args_repeats(cloner=None)
    @invalidate_these_args(invalidating_locs=(False,[0]),do_invalidate=lambda obj: obj.invalidate(),
                           validation_query=lambda obj: obj.is_valid())
    def combine_many(self, *others : ContainsIterator):
        """
        self then other
        """
        #pylint:disable=protected-access
        for other in others:
            self.__f = chain(self.__f, other.__f)

    def consume_to_list(self, ignore_validity=False) -> List[int]:
        """
        entire iterator consumed, left empty
        """
        if self.__invalid and not ignore_validity:
            raise ConsumedObjectError
        return_val = iter([])
        self.__f, return_val = return_val, list(self.__f)
        return return_val

    def consume_one(self, ignore_validity=False) -> Optional[int]:
        """
        one piece of iterator consumed
        """
        if self.__invalid and not ignore_validity:
            raise ConsumedObjectError
        return next(self.__f, None)

def test_2_objects():
    """
    what happens when have two places driving iteration
    """
    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    assert x.is_valid()
    assert y.is_valid()
    x.combine(y)
    assert x.is_valid()
    assert not y.is_valid()
    assert y.consume_to_list(True) == [4,5,6]
    assert x.consume_to_list() == [1,2,3]

    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    assert x.is_valid()
    assert y.is_valid()
    x.combine(y)
    assert x.is_valid()
    assert not y.is_valid()
    assert x.consume_to_list() == [1,2,3,4,5,6]
    errored = False
    try:
        assert not y.consume_to_list()
    except ConsumedObjectError:
        errored = True
    assert errored
    assert not y.consume_to_list(True)

    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    assert x.is_valid()
    assert y.is_valid()
    x.combine(y)
    assert x.is_valid()
    assert not y.is_valid()
    assert y.consume_one(True) == 4
    assert x.consume_to_list() == [1,2,3,5,6]
    errored = False
    try:
        assert not y.consume_to_list()
    except ConsumedObjectError:
        errored = True
    assert errored
    assert not y.consume_to_list(True)

    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    assert x.is_valid()
    assert y.is_valid()
    x.combine(y)
    assert x.is_valid()
    assert not y.is_valid()
    errored = False
    try:
        assert y.consume_one() == 4
    except ConsumedObjectError:
        errored = True
    assert errored
    assert y.consume_one(True) == 4
    assert y.consume_to_list(True) == [5,6]
    assert x.consume_to_list() == [1,2,3]

class ContainsIteratorAutoClone:
    """
    contains a private iterator
    combine/combine_many automatically clones, checks validity and invalidates
    """
    def __init__(self, initial_vals: List[int]):
        self.__f = iter(initial_vals)
        self.__invalid = False

    def clone(self):
        """
        a clone which can be independently driven
        """
        my_list = list(self.__f)
        to_return = ContainsIteratorAutoClone(my_list)
        self.__f = iter(my_list)
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
    @handle_args_repeats(cloner=lambda old_obj: old_obj.clone())
    @invalidate_these_args(invalidating_locs=(True,[1]),do_invalidate=lambda obj: obj.invalidate(),
                           validation_query=lambda obj: obj.is_valid())
    def combine(self, other : ContainsIterator):
        """
        self then other
        """
        #pylint:disable=protected-access
        self.__f = chain(self.__f, other.__f)

    #pylint:disable=no-value-for-parameter
    @handle_args_repeats(cloner=lambda old_obj: old_obj.clone())
    @invalidate_these_args(invalidating_locs=(False,[0]),do_invalidate=lambda obj: obj.invalidate(),
                           validation_query=lambda obj: obj.is_valid())
    def combine_many(self, *others : ContainsIterator):
        """
        self then other
        """
        for other in others:
            #pylint:disable=protected-access
            self.__f = chain(self.__f, other.__f)

    def consume_to_list(self, ignore_validity=False) -> List[int]:
        """
        entire iterator consumed, left empty
        """
        if self.__invalid and not ignore_validity:
            raise ConsumedObjectError
        return_val = iter([])
        self.__f, return_val = return_val, list(self.__f)
        return return_val

    def consume_one(self, ignore_validity=False) -> Optional[int]:
        """
        one piece of iterator consumed
        """
        if self.__invalid and not ignore_validity:
            raise ConsumedObjectError
        return next(self.__f, None)

def test_2_objects_autoclone():
    """
    what happens when have two places driving iteration
    """
    x = ContainsIteratorAutoClone([1,2,3])
    assert x.is_valid()
    y = ContainsIteratorAutoClone([4,5,6])
    assert y.is_valid()
    x.combine(y)
    assert x.is_valid()
    assert not y.is_valid()
    assert y.consume_to_list(True) == [4,5,6]
    assert x.consume_to_list() == [1,2,3]
    errored = False
    try:
        assert y.consume_to_list() == [4,5,6]
    except ConsumedObjectError:
        errored = True
    assert errored

    x = ContainsIteratorAutoClone([1,2,3])
    y = ContainsIteratorAutoClone([4,5,6])
    x.combine(y)
    assert x.consume_to_list() == [1,2,3,4,5,6]
    assert not y.consume_to_list(True)
    errored = False
    try:
        assert not y.consume_to_list()
    except ConsumedObjectError:
        errored = True
    assert errored

    x = ContainsIteratorAutoClone([1,2,3])
    y = ContainsIteratorAutoClone([4,5,6])
    x.combine(y)
    assert y.consume_one(True) == 4
    assert x.consume_to_list() == [1,2,3,5,6]
    assert not y.consume_to_list(True)

    x = ContainsIteratorAutoClone([1,2,3])
    y = ContainsIteratorAutoClone([4,5,6])
    x.combine(y)
    assert y.consume_one(True) == 4
    assert y.consume_to_list(True) == [5,6]
    assert x.consume_to_list() == [1,2,3]

def test_one_object_noclone():
    """
    what happens when have combining with self
    but the combine method wasn't given a cloner
    in the decorator
    """
    x = ContainsIterator([1,2,3])
    errored = False
    try:
        x.combine(x)
    except SameObjectError:
        errored = True
    assert errored

def test_one_object_autoclone():
    """
    what happens when have combining with self
    and automatically clone
    """
    x = ContainsIteratorAutoClone([1,2,3])
    x.combine(x)
    assert x.consume_to_list() == [1,2,3,1,2,3]

def test_combine_many():
    """
    test if decorator still works on many arguments
    """
    x = ContainsIterator([1,2,3])
    y = ContainsIterator([4,5,6])
    errored = False
    try:
        x.combine_many(y, x, x, y)
    except SameObjectError:
        errored = True
    assert errored
    errored = False
    try:
        x.combine_many(y, y)
    except SameObjectError:
        errored = True
    assert errored
    errored = False
    try:
        x.combine_many(x, x, x)
    except SameObjectError:
        errored = True
    assert errored
    errored = False
    try:
        x.combine_many(x)
    except SameObjectError:
        errored = True
    assert errored
    x.combine_many(y)
    assert x.consume_to_list() == [1,2,3,4,5,6]

    x = ContainsIteratorAutoClone([1,2,3])
    y = ContainsIteratorAutoClone([4,5,6])
    z = ContainsIteratorAutoClone([7])
    w = ContainsIteratorAutoClone([8])
    x.combine_many(y, x, x, y, z, z)
    assert x.is_valid()
    assert not y.is_valid()
    assert not z.is_valid()
    assert w.is_valid()
    assert x.consume_to_list() == [1,2,3,4,5,6,1,2,3,1,2,3,4,5,6,7,7]
