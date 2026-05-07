import json
import os
from datetime import datetime


class TodoManager:
    """待办事项管理器，负责数据的持久化和业务逻辑处理"""

    def __init__(self, data_file="todos.json"):
        self.data_file = data_file
        self.todos = self._load_todos()

    def _load_todos(self):
        """从 JSON 文件加载待办事项"""
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_todos(self):
        """将待办事项保存到 JSON 文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)

    def add_todo(self, title: str) -> dict:
        """
        添加一个新的待办事项
        
        Args:
            title: 待办事项的标题
            
        Returns:
            新创建的待办事项字典
        """
        if not title or not title.strip():
            raise ValueError("标题不能为空")
        
        new_todo = {
            "id": len(self.todos) + 1,
            "title": title.strip(),
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        self.todos.append(new_todo)
        self._save_todos()
        return new_todo

    def get_all_todos(self) -> list:
        """获取所有待办事项列表"""
        return self.todos.copy()

    def mark_completed(self, todo_id: int) -> dict:
        """
        标记某个待办事项为已完成
        
        Args:
            todo_id: 待办事项的 ID
            
        Returns:
            更新后的待办事项字典
            
        Raises:
            ValueError: 如果找不到对应的 ID
        """
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                self._save_todos()
                return todo.copy()
        raise ValueError(f"未找到 ID 为 {todo_id} 的待办事项")

    def delete_todo(self, todo_id: int) -> bool:
        """
        删除一个待办事项
        
        Args:
            todo_id: 待办事项的 ID
            
        Returns:
            是否删除成功
            
        Raises:
            ValueError: 如果找不到对应的 ID
        """
        original_length = len(self.todos)
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        
        if len(self.todos) == original_length:
            raise ValueError(f"未找到 ID 为 {todo_id} 的待办事项")
            
        self._save_todos()
        return True

    def clear_all(self):
        """清空所有待办事项"""
        self.todos = []
        self._save_todos()