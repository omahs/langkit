"""
This file contains general utility functions. It is basically the support
library for langkit, aggregating general python utilities that we could not
find in the standard library.
"""

from __future__ import absolute_import, division, print_function

from collections import defaultdict
from contextlib import contextmanager
from copy import copy
from functools import partial
import inspect
from itertools import takewhile
import sys

try:
    import gdb
except ImportError:
    gdb = None


class StructEq(object):
    """
    Mixin for structural equality.
    """
    def __eq__(self, other):
        if type(other) is type(self):
            if hasattr(self, "_eq_keys"):
                eq_keys = self._eq_keys
            elif hasattr(self, "_excl_eq_keys"):
                eq_keys = set(self.__dict__.keys()) ^ set(self._excl_eq_keys)
            else:
                return self.__dict__ == other.__dict__

            return all(v == other.__dict__[k] for k, v in self.__dict__
                       if k in eq_keys)

        return False


def unescape(char):
    """
    Unescape char if it is escaped.

    :param str char: An eventually escaped character.
    :rtype: str
    """
    if char[0] == "\\":
        return char[1:]
    return char


def copy_with(obj, **kwargs):
    """
    Copy an object, and add every key value association passed in kwargs to it.

    :param dict[str, Any] kwargs: key value associations to attach to the
        object.
    :param T obj: The object to copy.
    :rtype: T

    Example use::

        class A(object):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        inst = A(12, 15)
        inst_2 = copy_with(inst, a=16)
        print inst_2.a
        # Prints "16"
        print inst_2.b
        # Prints "12"
    """
    c = copy(obj)

    for k, v in kwargs.items():
        setattr(c, k, v)

    return c


def is_same(coll):
    """
    Helper function, returns True if every element in collection hashes to
    the same value.
    """
    return len(set(coll)) == 1


class Colors(object):
    """
    Utility escape sequences to color output in terminal.
    """
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GREY = '\033[97m'

    HEADER = MAGENTA
    OKBLUE = BLUE
    OKGREEN = GREEN
    WARNING = YELLOW
    FAIL = RED

    _enabled = True

    @classmethod
    def disable_colors(cls):
        """
        Reset color codes to empty strings.
        """
        for name in dir(cls):
            value = getattr(cls, name)
            if (all(c.isalpha() for c in name) and
                    name.upper() == name and
                    isinstance(value, basestring)):
                setattr(cls, name, '')


# Keep colors when we are running under GDB. Otherwise, disable colors as soon
# as one of stdout or stderr is not a TTY.
if not gdb and (not sys.stdout.isatty() or not sys.stderr.isatty()):
    Colors.disable_colors()


@contextmanager
def no_colors():
    """
    Context manager to disable colors for a given scope.
    """
    old_val, Colors._enabled = Colors._enabled, False
    yield
    Colors._enabled = old_val


def col(msg, color):
    """
    Utility function that return a string colored with the proper escape
    sequences, for VT100 compatible terminals.

    :param str msg: The message to print.
    :param color: An escape sequence corresponding to the proper color. Pick
        one in the Colors class.
    :rtype: str
    """
    if Colors._enabled:
        return "{0}{1}{2}".format(color, msg, Colors.ENDC)
    else:
        return msg


def printcol(msg, color):
    """
    Utility print function that will print `msg` in color `color`.
    :param basestring msg: The message to print.
    :param basestring color: The color escape sequence from the enum class
        Colors which represents the color to use.
    :return: The color-escaped string, resetting the color to blank at the end.
    :rtype: basestring
    """
    print(col(msg, color))

    # Colored messages are used to show the user how the compilation process is
    # going, so flushing on a regular basis matters. When \n-based flushing is
    # disabled (because of a pipe, for instance), force flushing here.
    sys.stdout.flush()


def common_ancestor(*classes):
    """
    Return the bottom-most common parent class for all `classes`.

    Note that this considers only the first parent for each class, as if there
    was only single inheritance.

    :param classes: The classes for which we are searching a common ancestor.
    :type classes: list[types.ClassType]
    :rtype: types.ClassType
    """
    def rmro(klass):
        single_mro = []
        cls = klass
        while True:
            single_mro.append(cls)
            try:
                cls = cls.__bases__[0]
            except IndexError:
                break
        return reversed(single_mro)

    result = list(takewhile(lambda a: len(set(a)) == 1,
                            zip(*map(rmro, classes))))[-1][0]
    return result


def memoized(func):
    """
    Decorator to memoize a function.
    This function must be passed only hashable arguments.

    :param func: The function to decorate.
    """
    cache = {}

    if not getattr(memoized, "caches", None):
        memoized.caches = []

    memoized.caches.append(cache)

    def wrapper(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        try:
            result = cache[key]
        except KeyError:
            result = func(*args, **kwargs)
            cache[key] = result
            result = result
        return result

    wrapper.reset_cache = lambda: cache.clear()

    return wrapper


def reset_memoized():
    if getattr(memoized, "caches", None):
        for cache in memoized.caches:
            cache.clear()


def type_check_exact(klass):
    """
    Return a predicate that will return true if its parameter is exactly egal
    to `klass`.

    :param type klass: Class to check against.
    :rtype: (T) -> bool
    """
    return lambda t: t and t == klass


def type_check(klass):
    """
    Return a predicate that will return true if its parameter is a subclass
    of `klass`.
    :param type klass: Class to check against.
    :rtype: (T) -> bool
    """
    return lambda t: t and issubclass(t, klass)


def type_check_instance(klass):
    """
    Return a predicate that will return true if its parameter is a subclass
    of `klass`.
    :param type klass: Class to check against.
    :rtype: (T) -> bool
    """
    return lambda t: isinstance(t, klass)


def dispatch_on_type(type, type_to_action_assocs, exception=None):
    """
    Dispatch on the type parameter, execute the corresponding action
    depending on the type. Every type in type_to_action_assocs will be
    tested in turn. If type is a subtype of one of them, then the
    corresponding action will be executed.

    :param type: The type to dispatch upon.

    :param type_to_action_assocs: An association of types to actions that
        returns something.
    :type type_to_action_assocs: list[(type, (type) -> T)]

    :param Exception exception: The exception to raise in case the type is
        not in the dispatch table.

    :rtype: T
    """
    exception = exception or Exception(
        "Error in dispatch_on_type: {} not handled".format(type)
    )
    for target_type, action in type_to_action_assocs:
        if issubclass(type, target_type):
            return action(type)
    raise exception


def assert_type(obj, typ):
    """
    Ensure that obj is a subclass or instance of type, depending on whether obj
    is a type or an instance. Return obj. This allows a few things compared to
    regular asserts:

    1. The type of the return is correctly inferred by Pycharm.
    2. You can use a "fluent interface" style for style checks, using::

        b = assert_type(c, int) + 15

    rather than::

        assert isinstance(c, int)
        b = c + 15

    3. Provides a relatively informative error message by default.

    :param Any obj: The object to check.
    :param T typ: Type parameter. The expected type of obj.
    :rtype: T
    """
    if issubclass(type(obj), type):
        assert issubclass(obj, typ), (
            "Wrong base type for type {}, expected {}".format(obj, typ)
        )
    else:
        assert isinstance(obj, typ), (
            "Wrong type for object {}, expected {}, found {}".format(
                obj, typ, type(obj)
            )
        )
    return obj


class TypeSet(object):
    """
    This class is an helper for when you need to check wether an abstract
    operation was fulfilled for a whole hierarchy of classes, given that if
    the operation is fulfilled for all subclasses, then we consider that it is
    done for the parent class.

    This allows to automate the logic of, for example, checking if abstract
    properties are overridden properly, or if a match expression handles all
    cases.
    """

    def __init__(self):
        # Working set of ASTNode subclasses for the types that are covered by
        # matchers. Updated as we go through the list of matchers.
        self.matched_types = set()

    def include(self, t):
        """
        Include a class and all of its subclasses.

        If t is the last subclass for some base class, this adds the parent
        subclass. This makes sense as once all concrete subclasses of the
        abstract A type are handled, it is true that A is handled.

        Return whether t was already present in self.

        :param ASTNode|None t: Type parameter.
        :rtype: bool
        """
        if t in self.matched_types:
            return True

        # Include "t" and all its subclasses
        self.matched_types.add(t)
        for child in t.subclasses:
            self.include(child)

        # Include its parents if all their children are matched
        parents = list(t.get_inheritance_chain())[:-1]
        for parent in reversed(parents):
            if parent in self.matched_types:
                break
            subclasses = set(parent.subclasses)
            if not subclasses.issubset(self.matched_types):
                break
            # If we reach this point, all parent's subclasses are matched,
            # so we can state that parent itself is always matched.
            self.matched_types.add(parent)

        return False

    def unmatched_types(self, t):
        """
        Return the set of t subclasses that are not matched by any matcher.

        Omit subclasses when none of them are matched: only the parent is
        returned in this case, so that we don't flood users with whole
        hierarchies of classes.

        :param ASTNode t: Type parameter.
        :rtype: set[ASTNode]
        """
        if t in self.matched_types:
            return set()

        subclasses = set(t.subclasses)
        if subclasses & self.matched_types:
            result = set()
            for cls in subclasses:
                result.update(self.unmatched_types(cls))
        else:
            result = {t}
        return result


def issubtype(type, parent_type):
    """
    Helper wrapper around issubclass, because issubclass will raise an
    exception if compared object is not a class, which is extremely tedious for
    us in langkit.

    :param type: The object or type to check against parent_type.
    :param type parent_type: The supposed parent_type of type.
    """
    return inspect.isclass(type) and issubclass(type, parent_type)


class DictProxy(object):
    """
    Util class to be able to access dict keys via the attribute notation in
    Python. Used in the property DSL.
    """
    def __init__(self, dct):
        self.dct = dct

    def __getattr__(self, attr):
        return self.dct[attr]


def not_implemented_error(self_or_cls, method):
    """
    Return a NotImplementedError instance to explain that `self or_cls` must
    override method `method`.

    :param self or_cls: Class that does not implement `method`, or the instance
        of such a class.
    :param method: Method object for the method that should be overriden.
    :rtype: NotImplementedError
    """
    cls = self_or_cls if inspect.isclass(self_or_cls) else type(self_or_cls)
    return NotImplementedError('{} must override method {}'.format(
        cls.__name__, method.__name__
    ))


class Log():
    """
    This class is a relatively generic logging handler. It includes decorators
    and context managers to make logging easier.
    """
    enabled = defaultdict(bool)
    nesting_level = 0

    @staticmethod
    def log_return(trace):
        """
        Decorates a function, so that its return value is logged.
        """
        def decorator(fn):
            def internal(*args, **kwargs):
                ret = fn(*args, **kwargs)
                Log.log(trace, "{} returned {}".format(fn.__name__, ret))
                return ret
            return internal
        return decorator

    @staticmethod
    def log(trace, *args, **kwargs):
        """
        Log arguments on given trace.
        """
        if Log.enabled[trace]:
            sys.stdout.write(col("[{}] ".format(trace), Colors.YELLOW))
            if Log.nesting_level:
                sys.stdout.write("  " * Log.nesting_level)
            print(*args, **kwargs)

    def logger(self, trace):
        """
        Return a logger function for the given trace.
        """
        return partial(self.log, trace)

    @staticmethod
    def enable(trace):
        Log.enabled[trace] = True

    @staticmethod
    @contextmanager
    def nest():
        """
        Context manager that will increase the nesting level by 1.
        """
        Log.nesting_level += 1
        yield
        Log.nesting_level -= 1

    @staticmethod
    def recursive(fn):
        """
        Decorator for recursive functions that use logging. Every call to the
        function will increase the nesting level by 1.
        """
        def internal(*args, **kwargs):
            with Log.nest():
                return fn(*args, **kwargs)
        return internal


def topological_sort(items):
    """
    'items' is an iterable of (item, dependencies) pairs, where 'dependencies'
    is an iterable of the same type as 'items'.

    If 'items' is a generator rather than a data structure, it should not be
    empty. Passing an empty generator for 'items' (zero yields before return)
    will cause topological_sort() to raise TopologicalSortFailure.

    An empty iterable (e.g. list, tuple, set, ...) produces no items but
    raises no exception.
    """
    provided = set()
    while items:
        remaining_items = []
        emitted = False
        for item, dependencies in items:
            dependencies = set(dependencies)
            if provided.issuperset(dependencies):
                yield item
                provided.add(item)
                emitted = True
            else:
                remaining_items.append((item, dependencies))
        assert(emitted)
        items = remaining_items
