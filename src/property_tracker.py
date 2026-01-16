from abc import ABC
import builtins
from typing import Any

from src.dynamic_property.dict import ObservableDict
from src.dynamic_property.list import ObservableList
from src.dynamic_property.set import ObservableSet


class PropertyTracker(ABC):
    def __new__(cls):
        cls.safe_type_check: bool = True
        cls.change_history: list[tuple[str, Any, Any]] = []
        cls.dynamic_properties_history: dict[str, list[dict[str, str]]] = {}
        cls.ignore_tracking: list[str]
        return super().__new__(cls)

    def _on_dynamic_property_change(
        self, name: str, action: str, index, value, old_values: Any = None
    ):
        print(name)
        if name not in self.dynamic_properties_history:
            self.dynamic_properties_history[name] = []
        self.dynamic_properties_history[name].append(
            {
                "action": action,
                "index": str(index),
                "new_value": value,
                "len_old_value": str(
                    old_values.__len__() if old_values is not None else None
                ),
            }
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in (
            "is_changed",
            "safe_type_check",
            "change_history",
            "dynamic_properties_history",
        ):
            return super().__setattr__(name, value)
        if name in self.__dict__ and name not in getattr(self, "ignore_tracking", []):
            match type(value):
                case builtins.set:
                    value = self.Set(name, value)
                case builtins.list:
                    value = self.List(name, value)
                case builtins.dict:
                    value = self.Dict(name, value)
                case _:
                    if self.safe_type_check and not isinstance(
                        value, self.__dict__[name].__class__
                    ):
                        raise Exception(
                            f"Type mismatch for property '{name}': expected {type(self.__dict__[name]).__name__}, got {type(value).__name__}"
                        ) from None
                    if self.__dict__[name] != value:
                        self.change_history.append((name, self.__dict__[name], value))
        return super().__setattr__(name, value)

    @property
    def is_changed(self) -> bool:
        return len(self.change_history) > 0

    def Set(self, property_name: str, value: set) -> set:
        """
        Docstring for Set

        :param self: Description
        :param name: Description
        :type name: str
        :param value: Description
        :type value: set
        :return: Description
        :rtype: set[Any]
        """
        return ObservableSet(self._on_dynamic_property_change, property_name, value)

    def List(self, property_name: str, value: list) -> list:
        """
        Docstring for List

        :param self: Description
        :param property_name: Description
        :type property_name: str
        :param value: Description
        :type value: list
        :return: Description
        :rtype: list[Any]
        """
        return ObservableList(self._on_dynamic_property_change, property_name, value)

    def Dict(self, property_name: str, value: dict) -> dict:
        """
        Docstring for Dict

        :param self: Description
        :param property_name: Description
        :type property_name: str
        :param value: Description
        :type value: dict
        :return: Description
        :rtype: dict[Any, Any]
        """
        return ObservableDict(self._on_dynamic_property_change, property_name, value)

    def reset_changed(self) -> None:
        self.change_history.clear()
        self.dynamic_properties_history.clear()
