from collections.abc import Callable, Set as TypingSet

class ObservableSet(set):
    """Set có thể theo dõi thay đổi"""
    
    def __init__(self, default_callback: Callable, property_name:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callbacks: list[Callable] = [default_callback]
        self.name = property_name
    
    def on_change(self, callback: Callable):
        """Đăng ký callback"""
        self._callbacks.append(callback)
        return callback
    
    def _notify(self, action: str, value, old_values: TypingSet | None):
        """Thông báo thay đổi"""
        for callback in self._callbacks:
            callback(self.name, action, "", value, old_values)
    
    def add(self, value):
        """Override add"""
        if value not in self:
            super().add(value)
            self._notify('add', value, None)
    
    def remove(self, value):
        """Override remove"""
        super().remove(value)
        self._notify('remove', value, None)
    
    def discard(self, value):
        """Override discard"""
        if value in self:
            super().discard(value)
            self._notify('discard', value, None)
    
    def pop(self):
        """Override pop"""
        value = super().pop()
        self._notify('pop', value, None)
        return value
    
    def clear(self):
        """Override clear"""
        old_data = set(self)
        super().clear()
        self._notify('clear', None, old_data)
    
    def update(self, *others):
        """Override update"""
        old_data = set(self)
        super().update(*others)
        new_items = self - old_data
        if new_items:
            self._notify('update', new_items, old_data)
    
    def intersection_update(self, *others):
        """Override intersection_update"""
        old_data = set(self)
        super().intersection_update(*others)
        removed_items = old_data - self
        if removed_items:
            self._notify('intersection_update', None, removed_items)
    
    def difference_update(self, *others):
        """Override difference_update"""
        old_data = set(self)
        super().difference_update(*others)
        removed_items = old_data - self
        if removed_items:
            self._notify('difference_update', None, removed_items)
    
    def symmetric_difference_update(self, other):
        """Override symmetric_difference_update"""
        old_data = set(self)
        super().symmetric_difference_update(other)
        self._notify('symmetric_difference_update', self, old_data)