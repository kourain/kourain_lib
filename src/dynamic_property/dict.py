from typing import Any, Callable


class ObservableDict(dict):
    """Dict có thể theo dõi thay đổi"""

    def __init__(self, default_callback: Callable, property_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callbacks: list[Callable] = [default_callback]
        self.name = property_name

    def on_change(self, callback: Callable):
        """Đăng ký callback"""
        self._callbacks.append(callback)
        return callback

    def _notify(
        self, action: str, key: Any = None, value: Any = None, old_value: Any = None
    ):
        """Thông báo thay đổi"""
        for callback in self._callbacks:
            callback(self.name, action, key, value, old_value)

    def __setitem__(self, key, value):
        """Bắt sự kiện set item"""
        if key in self:
            old_value = self[key]
            action = "update"
        else:
            old_value = None
            action = "add"

        super().__setitem__(key, value)
        self._notify(action, key, value, old_value)

    def __delitem__(self, key):
        """Bắt sự kiện delete item"""
        old_value = self[key]
        super().__delitem__(key)
        self._notify("delete", key, None, old_value)

    def pop(self, key, *args):
        """Override pop"""
        if key in self:
            old_value = self[key]
            result = super().pop(key, *args)
            self._notify("delete", key, None, old_value)
            return result
        return super().pop(key, *args)

    def popitem(self):
        """Override popitem"""
        key, value = super().popitem()
        self._notify("delete", key, None, value)
        return key, value

    def clear(self):
        """Override clear"""
        old_data = dict(self)
        super().clear()
        self._notify("clear", None, None, old_data)

    def update(self, *args, **kwargs):
        """Override update"""
        # Lưu trạng thái cũ
        old_data = dict(self)
        super().update(*args, **kwargs)

        # Thông báo cho từng item thay đổi
        for key, value in self.items():
            if key not in old_data:
                self._notify("add", key, value, None)
            elif old_data[key] != value:
                self._notify("update", key, value, old_data[key])

    def setdefault(self, key, default=None):
        """Override setdefault"""
        if key not in self:
            self[key] = default
        return self[key]
