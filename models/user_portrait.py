class user_portrait(dict):
    """可放入 set 的用户分段字典（基于4个字段去重）"""
    
    # 定义用于去重的字段
    _KEYS = ('user_value', 'user_status', 'product_type', 'industry')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 确保四个字段存在（可选）
        for key in self._KEYS:
            if key not in self:
                self[key] = None  # 或 raise KeyError
    
    def __hash__(self):
        # 基于四个字段的值生成哈希（元组是可哈希的）
        return hash(tuple(self[key] for key in self._KEYS))
    
    def __eq__(self, other):
        # 仅比较四个字段，不关心其他字段
        if not isinstance(other, user_portrait):
            return False
        return all(self[key] == other[key] for key in self._KEYS)