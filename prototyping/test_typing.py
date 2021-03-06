from unittest import TestCase, mock

from typing import Any
from typing import TypeVar, T, KT, VT, AnyStr
from typing import Union, Optional
from typing import Tuple
from typing import Callable
from typing import Generic
from typing import Undefined
from typing import cast


class Employee:
    pass


class Manager(Employee):
    pass


class Founder(Employee):
    pass


class ManagingFounder(Manager, Founder):
    pass


class AnyTests(TestCase):

    def test_any_instance(self):
        self.assertIsInstance(Employee(), Any)
        self.assertIsInstance(42, Any)
        self.assertIsInstance(None, Any)
        self.assertIsInstance(object(), Any)

    def test_any_subclass(self):
        self.assertTrue(issubclass(Employee, Any))
        self.assertTrue(issubclass(int, Any))
        self.assertTrue(issubclass(type(None), Any))
        self.assertTrue(issubclass(object, Any))

    def test_others_any(self):
        self.assertFalse(issubclass(Any, Employee))
        self.assertFalse(issubclass(Any, int))
        self.assertFalse(issubclass(Any, type(None)))
        # However, Any is a subclass of object (this can't be helped).
        self.assertTrue(issubclass(Any, object))

    def test_repr(self):
        self.assertEqual(repr(Any), 'typing.Any')

    def test_errors(self):
        with self.assertRaises(TypeError):
            issubclass(42, Any)
        with self.assertRaises(TypeError):
            Any[int]  # Any is not a generic type.

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class A(Any):
                pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Any()

    def test_cannot_subscript(self):
        with self.assertRaises(TypeError):
            Any[int]


class TypeVarTests(TestCase):

    def test_isinstance(self):
        self.assertNotIsInstance(42, T)
        self.assertIsInstance(b'b', AnyStr)
        self.assertIsInstance('s', AnyStr)
        self.assertNotIsInstance(42, AnyStr)

    def test_issubclass(self):
        self.assertTrue(issubclass(T, Any))
        self.assertFalse(issubclass(int, T))
        self.assertTrue(issubclass(bytes, AnyStr))
        self.assertTrue(issubclass(str, AnyStr))
        self.assertTrue(issubclass(T, T))
        self.assertTrue(issubclass(AnyStr, AnyStr))

    def test_repr(self):
        self.assertEqual(repr(T), '~T')
        self.assertEqual(repr(KT), '~KT')
        self.assertEqual(repr(VT), '~VT')
        self.assertEqual(repr(AnyStr), '~AnyStr')

    def test_no_redefinition(self):
        self.assertNotEqual(TypeVar('T'), TypeVar('T'))
        self.assertNotEqual(TypeVar('T', int, str), TypeVar('T', int, str))

    def test_subclass_as_unions(self):
        self.assertTrue(issubclass(TypeVar('T', int, str),
                                   TypeVar('T', int, str)))
        self.assertTrue(issubclass(TypeVar('T', int), TypeVar('T', int, str)))
        self.assertTrue(issubclass(TypeVar('T', int, str),
                                   TypeVar('T', str, int)))
        A = TypeVar('A', int, str)
        B = TypeVar('B', int, str, float)
        self.assertTrue(issubclass(A, B))
        self.assertFalse(issubclass(B, A))

    def test_cannot_subclass_vars(self):
        with self.assertRaises(TypeError):
            class V(TypeVar('T')):
                pass

    def test_cannot_subclass_var_itself(self):
        with self.assertRaises(TypeError):
            class V(TypeVar):
                pass

    def test_cannot_instantiate_vars(self):
        with self.assertRaises(TypeError):
            TypeVar('A')()

    def test_bind(self):
        self.assertNotIsInstance(42, T)  # Baseline.
        with T.bind(int):
            self.assertIsInstance(42, T)
            self.assertNotIsInstance(3.14, T)
            self.assertTrue(issubclass(int, T))
            self.assertFalse(issubclass(T, int))
            self.assertFalse(issubclass(float, T))
        self.assertNotIsInstance(42, T)  # Baseline restored.

    def test_bind_reuse(self):
        self.assertNotIsInstance(42, T)  # Baseline.
        bv = T.bind(int)
        with bv:
            self.assertIsInstance(42, T)  # Bound.
            self.assertNotIsInstance(3.14, T)
        self.assertNotIsInstance(42, T)  # Baseline restored.
        # Reusing bv will work.
        with bv:
            self.assertIsInstance(42, T)  # Bound.
            self.assertNotIsInstance(3.14, T)
            # Reusing bv recursively won't work.
            with self.assertRaises(TypeError):
                with bv:
                    self.assertFalse("Should not get here")
            # Rebinding T explicitly will work.
            with T.bind(float):
                self.assertIsInstance(3.14, T)
                self.assertNotIsInstance(42, T)
            # Now the previous binding should be restored.
            self.assertIsInstance(42, T)
            self.assertNotIsInstance(3.14, T)
        self.assertNotIsInstance(42, T)  # Baseline restored.

    def test_bind_fail(self):
        # This essentially tests what happens when __enter__() raises
        # an exception.  __exit__() won't be called, but the
        # VarBinding and the TypeVar are still in consistent states.
        bv = T.bind(int)
        with mock.patch('typing.TypeVar._bind', side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                with bv:
                    self.assertFalse("Should not get here")
        self.assertNotIsInstance(42, T)
        with bv:
            self.assertIsInstance(42, T)
        self.assertNotIsInstance(42, T)


class UnionTests(TestCase):

    def test_basics(self):
        u = Union[int, float]
        self.assertNotEqual(u, Union)
        self.assertIsInstance(42, u)
        self.assertIsInstance(3.14, u)
        self.assertTrue(issubclass(int, u))
        self.assertTrue(issubclass(float, u))

    def test_union_any(self):
        u = Union[Any]
        self.assertEqual(u, Any)
        u = Union[int, Any]
        self.assertEqual(u, Any)
        u = Union[Any, int]
        self.assertEqual(u, Any)

    def test_union_object(self):
        u = Union[object]
        self.assertEqual(u, object)
        u = Union[int, object]
        self.assertEqual(u, object)
        u = Union[object, int]
        self.assertEqual(u, object)

    def test_union_any_object(self):
        u = Union[object, Any]
        self.assertEqual(u, Any)
        u = Union[Any, object]
        self.assertEqual(u, Any)

    def test_unordered(self):
        u1 = Union[int, float]
        u2 = Union[float, int]
        self.assertEqual(u1, u2)

    def test_subclass(self):
        u = Union[int, Employee]
        self.assertIsInstance(Manager(), u)
        self.assertTrue(issubclass(Manager, u))

    def test_self_subclass(self):
        self.assertTrue(issubclass(Union[KT, VT], Union))
        self.assertFalse(issubclass(Union, Union[KT, VT]))

    def test_multiple_inheritance(self):
        u = Union[int, Employee]
        self.assertIsInstance(ManagingFounder(), u)
        self.assertTrue(issubclass(ManagingFounder, u))

    def test_single_class_disappears(self):
        t = Union[Employee]
        self.assertIs(t, Employee)

    def test_base_class_disappears(self):
        u = Union[Employee, Manager, int]
        self.assertEqual(u, Union[int, Employee])
        u = Union[Manager, int, Employee]
        self.assertEqual(u, Union[int, Employee])
        u = Union[Employee, Manager]
        self.assertIs(u, Employee)

    def test_weird_subclasses(self):
        u = Union[Employee, int, float]
        v = Union[int, float]
        self.assertTrue(issubclass(v, u))
        w = Union[int, Manager]
        self.assertTrue(issubclass(w, u))

    def test_union_union(self):
        u = Union[int, float]
        v = Union[u, Employee]
        self.assertEqual(v, Union[int, float, Employee])

    def test_repr(self):
        self.assertEqual(repr(Union), 'typing.Union')
        u = Union[Employee, int]
        self.assertEqual(repr(u), 'typing.Union[test_typing.Employee, int]')
        u = Union[int, Employee]
        self.assertEqual(repr(u), 'typing.Union[int, test_typing.Employee]')

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(Union):
                pass
        with self.assertRaises(TypeError):
            class C(Union[int, str]):
                pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Union()
        u = Union[int, float]
        with self.assertRaises(TypeError):
            u()

    def test_optional(self):
        o = Optional[int]
        u = Union[int, None]
        self.assertEqual(o, u)
        self.assertIsInstance(42, o)
        self.assertIsInstance(None, o)
        self.assertNotIsInstance(3.14, o)

    def test_empty(self):
        with self.assertRaises(TypeError):
            Union[()]


class TypeVarUnionTests(TestCase):

    def test_simpler(self):
        A = TypeVar('A', int, str, float)
        B = TypeVar('B', int, str)
        assert issubclass(A, A)
        assert issubclass(B, B)
        assert issubclass(B, A)
        assert issubclass(A, Union[int, str, float])
        assert issubclass(Union[int, str, float], A)
        assert issubclass(Union[int, str], B)
        assert issubclass(B, Union[int, str])
        assert not issubclass(A, B)
        assert not issubclass(Union[int, str, float], B)
        assert not issubclass(A, Union[int, str])

    def test_var_union_subclass(self):
        self.assertTrue(issubclass(T, Union[int, T]))
        self.assertTrue(issubclass(KT, Union[KT, VT]))

    def test_var_union(self):
        TU = TypeVar('TU', Union[int, float])
        self.assertIsInstance(42, TU)
        self.assertIsInstance(3.14, TU)
        self.assertNotIsInstance('', TU)
        with TU.bind(int):
            # The effective binding is the union.
            self.assertIsInstance(42, TU)
            self.assertIsInstance(3.14, TU)
            self.assertNotIsInstance('', TU)
        with self.assertRaises(TypeError):
            with TU.bind(str):
                self.assertFalse("Should not get here")

    def test_var_union_and_more_precise(self):
        TU = TypeVar('TU', Union[int, float], int)
        with TU.bind(int):
            # The binding is ambiguous, but the second alternative
            # is strictly more precise.  Choose the more precise match.
            # The effective binding is int.
            self.assertIsInstance(42, TU)
            self.assertNotIsInstance(3.14, TU)
            self.assertNotIsInstance('', TU)
        with TU.bind(float):
            # The effective binding is the union.
            self.assertIsInstance(42, TU)
            self.assertIsInstance(3.14, TU)
            self.assertNotIsInstance('', TU)

    def test_var_union_overlapping(self):
        TU = TypeVar('TU', Union[int, float], Union[float, str])
        with TU.bind(int):
            # The effective binding is the first union.
            self.assertIsInstance(42, TU)
            self.assertIsInstance(3.14, TU)
            self.assertNotIsInstance('', TU)
        with TU.bind(float):
            # The binding is ambiguous, but neither constraint is a
            # subclass of the other.  Choose the first match.
            # The effective binding is the first union.
            self.assertIsInstance(42, TU)
            self.assertIsInstance(3.14, TU)
            self.assertNotIsInstance('', TU)
        with TU.bind(str):
            # The effective binding is the second union.
            self.assertNotIsInstance(42, TU)
            self.assertIsInstance(3.14, TU)
            self.assertIsInstance('', TU)


class TupleTests(TestCase):

    def test_basics(self):
        self.assertIsInstance((42, 3.14, ''), Tuple)
        self.assertIsInstance((42, 3.14, ''), Tuple[int, float, str])
        self.assertIsInstance((42,), Tuple[int])
        self.assertNotIsInstance((3.14,), Tuple[int])
        self.assertNotIsInstance((42, 3.14), Tuple[int, float, str])
        self.assertNotIsInstance((42, 3.14, 100), Tuple[int, float, str])
        self.assertNotIsInstance((42, 3.14, 100), Tuple[int, float])
        self.assertTrue(issubclass(Tuple[int, str], Tuple))
        self.assertTrue(issubclass(Tuple[int, str], Tuple[int, str]))
        self.assertFalse(issubclass(int, Tuple))
        self.assertFalse(issubclass(Tuple[float, str], Tuple[int, str]))
        self.assertFalse(issubclass(Tuple[int, str, int], Tuple[int, str]))
        self.assertFalse(issubclass(Tuple[int, str], Tuple[int, str, int]))
        self.assertTrue(issubclass(tuple, Tuple))
        self.assertFalse(issubclass(Tuple, tuple))  # Can't have it both ways.

    def test_tuple_subclass(self):
        class MyTuple(tuple):
            pass
        self.assertTrue(issubclass(MyTuple, Tuple))

    def test_repr(self):
        self.assertEqual(repr(Tuple), 'typing.Tuple')
        self.assertEqual(repr(Tuple[()]), 'typing.Tuple[]')
        self.assertEqual(repr(Tuple[int, float]), 'typing.Tuple[int, float]')

    def test_errors(self):
        with self.assertRaises(TypeError):
            issubclass(42, Tuple)
        with self.assertRaises(TypeError):
            issubclass(42, Tuple[int])


class CallableTests(TestCase):

    def test_basics(self):
        c = Callable[[int, float], str]

        def flub(a: int, b: float) -> str:
            return str(a*b)

        def flob(a: int, b: int) -> str:
            return str(a*b)

        self.assertIsInstance(flub, c)
        self.assertNotIsInstance(flob, c)

    def test_self_subclass(self):
        self.assertTrue(issubclass(Callable[[int], int], Callable))
        self.assertFalse(issubclass(Callable, Callable[[int], int]))
        self.assertTrue(issubclass(Callable[[int], int], Callable[[int], int]))
        self.assertFalse(issubclass(Callable[[Employee], int],
                                    Callable[[Manager], int]))
        self.assertFalse(issubclass(Callable[[Manager], int],
                                    Callable[[Employee], int]))
        self.assertFalse(issubclass(Callable[[int], Employee],
                                    Callable[[int], Manager]))
        self.assertFalse(issubclass(Callable[[int], Manager],
                                    Callable[[int], Employee]))

    def test_eq_hash(self):
        self.assertEqual(Callable[[int], int], Callable[[int], int])
        self.assertEqual(len({Callable[[int], int], Callable[[int], int]}), 1)
        self.assertNotEqual(Callable[[int], int], Callable[[int], str])
        self.assertNotEqual(Callable[[int], int], Callable[[str], int])
        self.assertNotEqual(Callable[[int], int], Callable[[int, int], int])
        self.assertNotEqual(Callable[[int], int], Callable[[], int])
        self.assertNotEqual(Callable[[int], int], Callable)

    def test_with_none(self):
        c = Callable[[None], None]

        def flub(self: None) -> None:
            pass

        def flab(self: Any) -> None:
            pass

        def flob(self: None) -> Any:
            pass

        self.assertIsInstance(flub, c)
        self.assertIsInstance(flab, c)
        self.assertNotIsInstance(flob, c)  # Test contravariance.

    def test_with_subclasses(self):
        c = Callable[[Employee, Manager], Employee]

        def flub(a: Employee, b: Employee) -> Manager:
            return Manager()

        def flob(a: Manager, b: Manager) -> Employee:
            return Employee()

        self.assertIsInstance(flub, c)
        self.assertNotIsInstance(flob, c)

    def test_with_default_args(self):
        c = Callable[[int], int]

        def flub(a: int, b: float = 3.14) -> int:
            return a

        def flab(a: int, *, b: float = 3.14) -> int:
            return a

        def flob(a: int = 42) -> int:
            return a

        self.assertIsInstance(flub, c)
        self.assertIsInstance(flab, c)
        self.assertIsInstance(flob, c)

    def test_with_varargs(self):
        c = Callable[[int], int]

        def flub(*args) -> int:
            return 42

        def flab(*args: int) -> int:
            return 42

        def flob(*args: float) -> int:
            return 42

        self.assertIsInstance(flub, c)
        self.assertIsInstance(flab, c)
        self.assertNotIsInstance(flob, c)

    def test_with_method(self):

        class C:

            def imethod(self, arg: int) -> int:
                self.last_arg = arg
                return arg + 1

            @classmethod
            def cmethod(cls, arg: int) -> int:
                cls.last_cls_arg = arg
                return arg + 1

            @staticmethod
            def smethod(arg: int) -> int:
                return arg + 1

        ct = Callable[[int], int]
        self.assertIsInstance(C().imethod, ct)
        self.assertIsInstance(C().cmethod, ct)
        self.assertIsInstance(C.cmethod, ct)
        self.assertIsInstance(C().smethod, ct)
        self.assertIsInstance(C.smethod, ct)
        self.assertIsInstance(C.imethod, Callable[[Any, int], int])

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):

            class C(Callable):
                pass

        with self.assertRaises(TypeError):

            class C(Callable[[int], int]):
                pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Callable()
        c = Callable[[int], str]
        with self.assertRaises(TypeError):
            c()


XK = TypeVar('XK', str, bytes)
XV = TypeVar('XV')


class SimpleMapping(Generic[XK, XV]):

    def __getitem__(self, key: XK) -> XV:
        ...

    def __setitem__(self, key: XK, value: XV):
        ...

    def get(self, key: XK, default: XV = None) -> XV:
        ...


class MySimpleMapping(SimpleMapping):

    def __init__(self):
        self.store = {}

    def __getitem__(self, key: str):
        return self.store[key]

    def __setitem__(self, key: str, value):
        self.store[key] = value

    def get(self, key: str, default=None):
        try:
            return self.store[key]
        except KeyError:
            return default


class GenericTests(TestCase):

    def test_basics(self):
        X = SimpleMapping[str, Any]
        Y = SimpleMapping[AnyStr, str]
        X[str, str]
        Y[str, str]
        with self.assertRaises(TypeError):
            X[int, str]
        with self.assertRaises(TypeError):
            Y[str, bytes]

    def test_repr(self):
        self.assertEqual(repr(SimpleMapping),
                         __name__ + '.' + 'SimpleMapping[~XK, ~XV]')
        self.assertEqual(repr(MySimpleMapping),
                         __name__ + '.' + 'MySimpleMapping[~XK, ~XV]')
        A = TypeVar('A', str)  # Must be a subclass of XK.
        B = TypeVar('B')

        class X(SimpleMapping[A, B]):
            pass

        self.assertEqual(repr(X).split('.')[-1], 'X[~A, ~B]')

    def test_errors(self):
        with self.assertRaises(TypeError):
            class C(SimpleMapping[XK, Any]):
                pass

    def test_repr_2(self):

        class C(Generic[T]):
            pass

        assert C.__module__ == __name__
        assert C.__qualname__ == 'GenericTests.test_repr_2.<locals>.C'
        assert repr(C).split('.')[-1] == 'C[~T]'
        X = C[int]
        assert X.__module__ == __name__
        assert X.__qualname__ == 'C'
        assert repr(X).split('.')[-1] == 'C[int]'

        class Y(C[int]):
            pass

        assert Y.__module__ == __name__
        assert Y.__qualname__ == 'GenericTests.test_repr_2.<locals>.Y'
        assert repr(Y).split('.')[-1] == 'Y[int]'

    def test_eq_1(self):
        assert Generic == Generic
        assert Generic[T] == Generic[T]
        assert Generic[KT] != Generic[VT]

    def test_eq_2(self):

        class A(Generic[T]):
            pass

        class B(Generic[T]):
            pass

        assert A == A
        assert A != B
        assert A[T] == A[T]
        assert A[T] != B[T]


class UndefinedTest(TestCase):

    def test_basics(self):
        x = Undefined(int)
        x = Undefined(Any)
        x = Undefined(Union[int, str])
        x = Undefined(None)

    def test_errors(self):
        with self.assertRaises(TypeError):
            x = Undefined(42)
        u = Undefined(int)
        with self.assertRaises(TypeError):
            {u: 42}

    def test_repr(self):
        self.assertEqual(repr(Undefined(Any)), 'typing.Undefined(typing.Any)')


class CastTest(TestCase):

    def test_basics(self):
        assert cast(int, 42) == 42
        assert cast(float, 42) == 42
        assert type(cast(float, 42)) is int
        assert cast(Any, 42) == 42
        assert cast(list, 42) == 42
        assert cast(Union[str, float], 42) == 42
        assert cast(AnyStr, 42) == 42
        assert cast(None, 42) == 42

    def test_errors(self):
        with self.assertRaises(TypeError):
            cast(42, 42)
        with self.assertRaises(TypeError):
            cast('hello', 42)


class ForwardRefTest(TestCase):

    def test_basics(self):

        class Node(Generic[T]):
            pass  # Foward reference

        save_Node = Node

        class Node(Generic[T]):

            def __init__(self, label: T):
                self.label = label
                self.left = self.right = None

            def add_left(self, node: Optional[Node[T]]):
                self.left = node

        assert Node is save_Node

        t = Node[int]
        ann = t.add_left.__annotations__
        assert ann['node'] == Optional[Node[T]]
