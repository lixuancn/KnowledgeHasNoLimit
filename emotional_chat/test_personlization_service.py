# 测试代码
from backend.services.personlization_service import PersonalizationService
import logging
import json
from backend.services.prompt_composer import PromptComposer

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = PersonalizationService()
    
    # 测试默认配置
    print("=" * 60)
    print("测试1: 获取默认配置")
    print("=" * 60)
    default_config = service._get_default_config("test_user")
    print(json.dumps(default_config, ensure_ascii=False, indent=2))
    
    # 测试Prompt生成（不需要数据库）
    print("\n" + "=" * 60)
    print("测试2: 生成默认Prompt")
    print("=" * 60)
    composer = PromptComposer(default_config)
    prompt = composer.compose(
        context="用户说：今天心情不太好",
        emotion_state={
            "emotion": "sad",
            "intensity": 6.5
        }
    )
    print(prompt)