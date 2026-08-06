from abc import ABCMeta, abstractmethod, update_abstractmethods
from types import FunctionType


class _InterfaceMeta(ABCMeta):
    def __new__(metaclass, name, bases, namespace):
        if "Interface" in globals() and Interface in bases:
            for member_name, member in tuple(namespace.items()):
                if not member_name.startswith("__") and isinstance(member, FunctionType):
                    namespace[member_name] = abstractmethod(member)
        return super().__new__(metaclass, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if bases:
            for attribute in cls.__annotations__:
                if attribute not in cls.__dict__:
                    def getter(self):
                        pass

                    setattr(cls, attribute, property(abstractmethod(getter)))
            update_abstractmethods(cls)


class Interface(metaclass=_InterfaceMeta):
    pass
