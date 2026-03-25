import json
from backend.evaluation_engine import EvaluationEngine

# 测试评估引擎
engine = EvaluationEngine()

test_cases = [
    {
        "user_message": "我今天工作被批评了，感觉很沮丧",
        "bot_response": "听起来你今天遇到了挫折。被批评确实让人难受。我在这里倾听，你愿意说说具体发生了什么吗？",
        "user_emotion": "sad",
        "emotion_intensity": 7.0
    },
    {
        "user_message": "我感觉很焦虑，不知道怎么办",
        "bot_response": "你应该多运动，运动可以缓解焦虑。",
        "user_emotion": "anxious",
        "emotion_intensity": 8.0
    }
]

print("\n" + "="*80)
print("开始测试评估引擎...")
print("="*80 + "\n")

for i, test_case in enumerate(test_cases, 1):
    print("测试案例 {}:".format(i))
    print("-" * 80)
    result = engine.evaluate_response(**test_case)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n")

# 测试Prompt对比
print("\n" + "="*80)
print("测试Prompt对比功能...")
print("="*80 + "\n")

comparison = engine.compare_prompts(
    user_message="我今天心情不太好",
    responses={
        "简短回应": "哦，怎么了？",
        "共情回应": "听起来你今天遇到了一些不愉快的事情。我在这里倾听，你愿意说说发生了什么吗？",
        "建议型回应": "心情不好的时候可以出去散散步，或者找朋友聊聊天。"
    },
    user_emotion="sad",
    emotion_intensity=6.0
)

print(json.dumps(comparison, indent=2, ensure_ascii=False))