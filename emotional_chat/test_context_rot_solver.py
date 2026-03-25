from multiprocessing.spawn import _main
from backend.services.context_rot_solver import ContextCompactionStrategy

if __name__ == "__main__":
    # 测试上下文压缩策略
    strategy = ContextCompactionStrategy()
    
    # 示例工具调用
    tool_call = {
        "tool_name": "write_file",
        "arguments": {
            "file_path": "/path/to/file.txt",
            "content": "Hello, World!"
        }
    }
    
    # 压缩工具调用
    compacted = strategy.compact_tool_call(tool_call)
    print(compacted)
