import json
from backend.emotion_analyzer import EmotionAnalyzer


# 测试情感分析器
analyzer = EmotionAnalyzer()

# 测试情感分析
test_messages = [
    "我今天很高兴，收到了一份礼物！",
    "工作压力很大，感觉很焦虑。",
    "今天天气很好，心情不错。",
    "和朋友吵架了，很生气。",
    "今天是普通的一天，没什么特别的。"
]

for message in test_messages:
    print(f"\n分析消息: {message}")
    result = analyzer.analyze_emotion(message)
    print(f"情感分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试关键词分析
    keyword_result = analyzer._keyword_based_analysis(message)
    print(f"关键词分析结果: {json.dumps(keyword_result, ensure_ascii=False, indent=2)}")

    # 生成共情回应
    response = analyzer.generate_empathetic_response(message, result)
    print(f"共情回应: {json.dumps(response, ensure_ascii=False, indent=2)}")