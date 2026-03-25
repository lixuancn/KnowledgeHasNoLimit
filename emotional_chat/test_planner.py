# 使用示例
import json
from backend.modules.agent.core.agent.planner import Planner

if __name__ == "__main__":
    # 创建规划器
    planner = Planner()
    
    # 模拟用户输入和上下文
    user_input = "我最近睡不好，怎么办？"
    context = {
        "user_id": "user_123",
        "perception": {
            "emotion": "焦虑",
            "emotion_intensity": 7.5,
            "intent": "problem_solving"
        },
        "memories": []
    }
    
    # 生成执行计划
    import asyncio
    plan = asyncio.run(planner.plan(user_input, context))
    
    print("执行计划：")
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))