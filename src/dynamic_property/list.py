from typing import Any, Callable, SupportsIndex


class ObservableList(list):
    """List có thể theo dõi thay đổi"""

    def __init__(self, default_callback: Callable, property_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callbacks: list[Callable] = [default_callback]
        self.name = property_name

    def on_change(self, callback: Callable):
        """Đăng ký callback"""
        self._callbacks.append(callback)
        return callback

    def _notify(
        self,
        action: str,
        index: SupportsIndex | slice | None = None,
        value: Any = None,
        old_value: Any = None,
    ):
        """Thông báo thay đổi"""
        for callback in self._callbacks:
            callback(self.name, action, index if isinstance(index, (int, slice)) else None, value, old_value)

    def __setitem__(self, index, value):
        """Bắt sự kiện set item"""
        if isinstance(index, slice):
            old_values = self[index]
            super().__setitem__(index, value)
            self._notify("slice_update", index, value, old_values)
        else:
            old_value = self[index] if 0 <= index < len(self) else None
            super().__setitem__(index, value)
            self._notify("update", index, value, old_value)

    def __delitem__(self, index):
        """Bắt sự kiện delete item"""
        if isinstance(index, slice):
            old_values = self[index]
            super().__delitem__(index)
            self._notify("slice_delete", index, None, old_values)
        else:
            old_value = self[index]
            super().__delitem__(index)
            self._notify("delete", index, None, old_value)

    def append(self, value):
        """Override append"""
        index = len(self)
        super().append(value)
        self._notify("append", index, value, None)

    def extend(self, values):
        """Override extend"""
        start_index = len(self)
        super().extend(values)
        self._notify("extend", start_index, list(values), None)

    def insert(self, index, value):
        """Override insert"""
        super().insert(index, value)
        self._notify("insert", index, value, None)

    def remove(self, value):
        """Override remove"""
        try:
            index = self.index(value)
            super().remove(value)
            self._notify("remove", index, None, value)
        except ValueError:
            raise

    def pop(self, index: SupportsIndex = -1):
        """Override pop"""
        old_value = self[index]
        result = super().pop(index)
        self._notify("pop", index, None, old_value)
        return result

    def clear(self):
        """Override clear"""
        old_data = list(self)
        super().clear()
        self._notify("clear", None, None, old_data)

    def sort(self, *args, **kwargs):
        """Override sort"""
        old_data = list(self)
        super().sort(*args, **kwargs)
        self._notify("sort", None, list(self), old_data)

    def reverse(self):
        """Override reverse"""
        old_data = list(self)
        super().reverse()
        self._notify("reverse", None, list(self), old_data)
