# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = AdvancedSentimentAnalyzer(use_transformers=False)
    
    # 测试用例
    test_cases = [
        "今天好累啊，工作压力太大了。",
        "我升职啦！太开心了！",
        "明天要面试，好紧张啊...",
        "感觉一个人好孤单，没人理解我。",
        "谢谢你一直陪伴我，很感激。"
    ]
    
    print("\n===== 情感分析测试 =====\n")
    for i, text in enumerate(test_cases, 1):
        result = analyzer.analyze(text, user_id="test_user")
        
        print(f"测试 {i}: {text}")
        print(f"  情绪: {result['emotion']} (置信度: {result['confidence']})")
        print(f"  强度: {result['intensity']}/10")
        print(f"  极性: {result['polarity']}")
        print(f"  方法: {result['method']}")
        print(f"  建议: {result['suggestions'][0]}")
        print()
    
    # 测试情绪趋势
    print("\n===== 情绪趋势分析 =====\n")
    trend = analyzer.get_emotion_trend("test_user")
    print(f"趋势: {trend['trend']}")
    print(f"平均强度: {trend['average_intensity']}")
    print(f"主导情绪: {trend['dominant_emotion']}")
    print(f"情绪分布: {trend['emotion_distribution']}")
    if trend['warning']:
        print(f"⚠️ 警告: {trend['warning']}")
