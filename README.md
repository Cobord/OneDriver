# Motivation

In my plabic package (https://pypi.org/project/plabic/), I had a class which had a private iterator in my implementation of shuffle algebra calculations

But then if I did the shuffle product of x and x, those iterators would be both driven together rather than separately
Simlarly if I did x and y, then used y somehere else, the x iterator which should have had all of x and y information
would be missing some pieces depending on how the y iterator had been driven.

# Errors

So we have errors that cover this kind of situation. The first being SameObjectError and the latter being ConsumedObjectError

# Cloning

Suppose we provide a way of cloning the objects so that the closures/iterators contained are separate now. Then the two functions
avoid_common_pointers and avoid_this_pointer can fix up the argument lists to that combining function which expects all distinct objects.
If there are no repeats, it does not do anything and does not even need to ever try to call that optional cloning function.
If there are repeats, it will call the cloning function appropriately giving the new list of arguments.

# Decorators

Assumes that the function being called has all of it's args as that same type T
and none of the kwargs have T in them that need cloning

## handle_args_repeats

if you provide the cloner function on T and it will call that cloner on any repeated arguments in args
if you don't provide the cloner and there are repeats will raise the SameObjectError
if you don't provide the cloner and there are no repeats, there will not be an error

## invalidate_these_args

Either provide
- a list of argument numbers that become invalid after this function
- a list of argument numbers that remain valid after this function with the rest becoming invalid

Also need the function which does the invalidation and a way to query the validity

This makes sure all of the args are valid and then calls the function assuming that was the case
After this, the args which are supposed to become invalid are invalidated