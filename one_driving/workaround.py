"""
work arounds for two mutable references
inputs to functions thought of as having taken ownership
so anybody still with that pointer has results that can't be
relied on
e.g.
    y += x
    x is no longer a good object because of the class x,y belong too
    and the way __iadd__ was written in that class
"""

from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar

T = TypeVar("T")

def list_duplicates(seq : Iterable[T]):
    """
    which indices in the sequence were duplicates of something already seen
    """
    tally : Dict[T,List[int]] = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items()
            if len(locs)>1)

def avoid_common_pointers(seq: List[T],
                          how_to_clone: Optional[Callable[[T],T]] = None) \
                            -> Tuple[bool,List[int],List[T]]:
    """
    if any of the sequence are pointing to the same object
    do the requisite clone on the duplicates if have that function
    """
    how_to_clone_nonexistant = how_to_clone is None
    which_cloned = []
    for (_id,idces_seen) in list_duplicates((id(z) for z in seq)):
        the_unoriginals = idces_seen[1:]
        for idx in the_unoriginals:
            if how_to_clone_nonexistant:
                return (False,[],seq)
            which_cloned.append(idx)
            seq[idx] = how_to_clone(seq[idx])
    return (True,which_cloned,seq)

def avoid_this_pointer(what_to_avoid: T, seq: List[T],
                          how_to_clone: Optional[Callable[[T],T]] = None) -> \
                            Tuple[bool,List[int],List[T]]:
    """
    any in seq that has the same id as what_id, clone it if possible
    """
    the_unoriginals = (idx for idx,z in enumerate(seq) if id(z)==id(what_to_avoid))
    which_cloned = []
    how_to_clone_nonexistent = how_to_clone is None
    for idx in the_unoriginals:
        if how_to_clone_nonexistent:
            return (False,[],seq)
        which_cloned.append(idx)
        seq[idx] = how_to_clone(seq[idx])
    return (True,which_cloned,seq)

def parameterized(dec):
    """
    for parameterized decorators
    """
    def layer(*args,**kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

@parameterized
def handle_args_repeats(f : Callable[...,Any], cloner: Optional[Callable[[T],T]]):
    """
    if f takes args which are all instances of T
    then make sure they are different instances
    if not, either fix the problem with cloner
    or if no cloner is provided, raise SameObjectError
    how to use
    @method_repeats_decorator(None)
    @method_repeats_decorator(lambda old_obj: old_obj.clone())
    or whatever function does cloning
    the type annotation is lacking here because the ... in f
    should only be T's in the args and no T's in the kwargs
    """
    def wrapper(*args,**kwargs):
        (success, _, new_args) = avoid_common_pointers(list(args), cloner)
        if success:
            return f(*new_args,**kwargs)
        raise SameObjectError

    return wrapper

@parameterized
def invalidate_these_args(f : Callable[...,Any],
                          invalidating_locs: Tuple[bool,List[int]],
                          do_invalidate: Callable[[T],None],
                          validation_query: Callable[[T],bool]):
    """
    if f takes args which are all instances of T
    then after cloning with above decorator
    marks
    now have distinct objects in args
    make sure they are all valid according to the validation query
    if not raise ConsumedObjectError
    then do f as normally
    finally call do_invalidate on the appropriate arguments
    so that they won't be used again
    """
    def wrapper(*args,**kwargs):
        #pylint:disable=protected-access
        if not all(validation_query(cur_arg) for cur_arg in args):
            raise ConsumedObjectError
        return_value = f(*args,**kwargs)
        invalidating, which_idces = invalidating_locs
        if not invalidating:
            # only these ones stay valid and the rest are invalidating
            new_which_idces = [i for i in range(len(args)) if i not in which_idces]
            which_idces = new_which_idces
        for idx in which_idces:
            do_invalidate(args[idx])
        return return_value

    return wrapper

class SameObjectError(ValueError):
    """
    the two objects are exactly the same
    so lazy properties inside them won't behave correctly
    when we have a function that expects two different
    values of the same type
    """

class ConsumedObjectError(ValueError):
    """
    this object has been consumed by being the argument
    in another method, so it should be garbage collected
    already (or at least ready for garbage collection if that hasn't happened yet)
    but we don't have any ownership semantics to enforce not reusing
    so we resort to throwing an exception
    """
