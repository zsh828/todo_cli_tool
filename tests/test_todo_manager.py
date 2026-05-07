import os
import pytest
import tempfile
import json
from src.todo_manager import TodoManager


@pytest.fixture
def temp_data_file():
    """创建一个临时文件用于测试数据持久化"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('[]')
        temp_path = f.name
    yield temp_path
    # 清理临时文件
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def manager(temp_data_file):
    """创建 TodoManager 实例"""
    return TodoManager(data_file=temp_data_file)


class TestAddTodo:
    def test_add_valid_todo(self, manager):
        """测试添加有效的待办事项"""
        result = manager.add_todo("Buy groceries")
        assert result["title"] == "Buy groceries"
        assert result["completed"] is False
        assert "id" in result
        assert "created_at" in result
        assert result["id"] == 1
        
        # 验证数据已保存
        todos = manager.get_all_todos()
        assert len(todos) == 1
        assert todos[0]["title"] == "Buy groceries"

    def test_add_multiple_todos(self, manager):
        """测试添加多个待办事项，ID 应递增"""
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")
        
        todos = manager.get_all_todos()
        assert len(todos) == 2
        assert todos[0]["id"] == 1
        assert todos[1]["id"] == 2

    def test_add_empty_title_raises_error(self, manager):
        """测试添加空标题时抛出异常"""
        with pytest.raises(ValueError, match="标题不能为空"):
            manager.add_todo("")

    def test_add_whitespace_only_title_raises_error(self, manager):
        """测试添加仅包含空白字符的标题时抛出异常"""
        with pytest.raises(ValueError, match="标题不能为空"):
            manager.add_todo("   ")

    def test_add_todo_trims_whitespace(self, manager):
        """测试添加待办事项时自动去除首尾空格"""
        result = manager.add_todo("  Trimmed Task  ")
        assert result["title"] == "Trimmed Task"


class TestGetAllTodos:
    def test_get_all_empty_list(self, manager):
        """测试初始状态下获取待办事项列表为空"""
        todos = manager.get_all_todos()
        assert todos == []

    def test_get_all_returns_copy(self, manager):
        """测试获取的列表是副本，修改不影响内部状态"""
        manager.add_todo("Original Task")
        todos = manager.get_all_todos()
        todos.clear()
        
        internal_todos = manager.get_all_todos()
        assert len(internal_todos) == 1
        assert internal_todos[0]["title"] == "Original Task"


class TestMarkCompleted:
    def test_mark_completed_success(self, manager):
        """测试成功标记待办事项为已完成"""
        added = manager.add_todo("Complete me")
        todo_id = added["id"]
        
        result = manager.mark_completed(todo_id)
        assert result["completed"] is True
        assert result["id"] == todo_id
        
        # 验证持久化
        todos = manager.get_all_todos()
        assert todos[0]["completed"] is True

    def test_mark_completed_invalid_id_raises_error(self, manager):
        """测试标记不存在的 ID 时抛出异常"""
        with pytest.raises(ValueError, match="未找到 ID 为 999 的待办事项"):
            manager.mark_completed(999)

    def test_mark_already_completed(self, manager):
        """测试重复标记已完成状态"""
        added = manager.add_todo("Already done")
        todo_id = added["id"]
        
        manager.mark_completed(todo_id)
        manager.mark_completed(todo_id)  # Should not raise error
        
        todos = manager.get_all_todos()
        assert todos[0]["completed"] is True


class TestDeleteTodo:
    def test_delete_existing_todo(self, manager):
        """测试成功删除存在的待办事项"""
        added = manager.add_todo("To Delete")
        todo_id = added["id"]
        
        result = manager.delete_todo(todo_id)
        assert result is True
        
        todos = manager.get_all_todos()
        assert len(todos) == 0

    def test_delete_non_existent_todo_raises_error(self, manager):
        """测试删除不存在的 ID 时抛出异常"""
        with pytest.raises(ValueError, match="未找到 ID 为 999 的待办事项"):
            manager.delete_todo(999)

    def test_delete_preserves_other_todos(self, manager):
        """测试删除一个待办事项后，其他待办事项保持不变"""
        t1 = manager.add_todo("Keep 1")
        t2 = manager.add_todo("Keep 2")
        t3 = manager.add_todo("Delete 3")
        
        manager.delete_todo(t3["id"])
        
        todos = manager.get_all_todos()
        assert len(todos) == 2
        titles = [t["title"] for t in todos]
        assert "Keep 1" in titles
        assert "Keep 2" in titles
        assert "Delete 3" not in titles

    def test_delete_updates_ids_logic(self, manager):
        """注意：当前实现中 ID 不会重新分配，只检查删除操作本身"""
        t1 = manager.add_todo("First")
        t2 = manager.add_todo("Second")
        
        manager.delete_todo(t1["id"])
        
        todos = manager.get_all_todos()
        assert len(todos) == 1
        assert todos[0]["id"] == t2["id"]  # ID 保持不变


class TestPersistence:
    def test_data_persists_after_reload(self, temp_data_file):
        """测试数据在重新加载实例后依然存在"""
        mgr1 = TodoManager(data_file=temp_data_file)
        mgr1.add_todo("Persistent Task")
        
        # 创建新实例模拟程序重启
        mgr2 = TodoManager(data_file=temp_data_file)
        todos = mgr2.get_all_todos()
        
        assert len(todos) == 1
        assert todos[0]["title"] == "Persistent Task"


class TestClearAll:
    def test_clear_all_removes_all_todos(self, manager):
        """测试清空所有待办事项"""
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")
        
        manager.clear_all()
        
        todos = manager.get_all_todos()
        assert len(todos) == 0

    def test_clear_all_on_empty_list(self, manager):
        """测试在空列表上执行清空操作"""
        manager.clear_all()
        todos = manager.get_all_todos()
        assert len(todos) == 0