from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.modules.llm.core.llm import LLM

import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

# 数据库和模型
from backend.database import DatabaseManager
# 情感分析器
from backend.emotion_analyzer import EmotionAnalyzer
# 模型
from backend.models import ChatRequest, ChatResponse
# 导入向量数据库
from backend.vector_store import VectorStore
# 导入心语Prompt配置
from backend.xinyu_prompt import (
    get_system_prompt,
    validate_and_filter_input,
    get_conversation_template
)

class SimpleEmotionalChatEngine:
    def __init__(self):
        """
        初始化简单情感聊天引擎
        """
        self.db_manager = DatabaseManager()
        print("✓ 关系数据库 (MySQL) 初始化成功")
        self.vector_store = VectorStore()
        print("✓ 向量数据库 (阿里云dashvector) 初始化成功")
        # 初始化LLM
        self.llm = LLM().ChatOpenAI()
        print("✓ LLM 初始化成功")
        # 初始化情感分析器
        self.emotion_analyzer = EmotionAnalyzer()
        print("✓ 情感分析器 初始化成功")
        # 初始化对话模板
        self.template = get_conversation_template().format(system_prompt=get_system_prompt())
        # 创建提示模板和链（LCEL表达式）
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.output_parser = StrOutputParser()
        # 使用链式表达创建完整的处理链
        self.chain = self.prompt | self.llm | self.output_parser
        print("✓ LangChain LCEL 链初始化成功")

    def get_openai_response(self, user_input, user_id, session_id):
        """使用 LangChain LCEL 链生成回应"""
        # 安全检查
        is_safe, warning = validate_and_filter_input(user_input)
        if not is_safe:
            return warning
        
        # 构建历史对话（短期记忆 - MySQL）
        with self.db_manager as db:
            recent_messages = db.get_session_messages(session_id, limit=10)
            history_text = ""
            for msg in reversed(recent_messages[-5:]):  # 最近5条消息
                history_text += "{}: {}\n".format('用户' if msg.role == 'user' else '心语', msg.content)
        
        # 从向量数据库检索相似对话（长期记忆）
        long_term_context = ""
        try:
            print(f"User input: {user_input}")
            # 检索相似的历史对话（跨会话）
            similar_conversations = self.vector_store.search_similar_conversation(
                query=user_input,
                session_id=session_id,  # 不限制会话，检索所有历史
                topk=3
            )
            if similar_conversations and similar_conversations.output:
                long_term_context = "\n相关历史对话参考：\n"
                for doc in similar_conversations.output[:2]:  # 取前2个最相似的
                    long_term_context += "- {}\n".format(doc.fields['message'][:100])  # 限制长度
                long_term_context += "\n"
            print(f"Long term context: {long_term_context}")
        except Exception as e:
            print("向量检索失败: {}".format(e))
        
        try:
            # 4. 使用链生成回应 (chain.invoke) - 包含长期记忆
            response = self.chain.invoke({
                "long_term_memory": long_term_context,
                "history": history_text.strip(),
                "user_input": user_input
            })
            print(f"chain response: {response}")
            return response
        except Exception as e:
            print("LangChain调用失败: {}，尝试兜底".format(e))
        
        # 兜底
        return self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input, emotion_data=None):
        """提供备选回应当API调用失败时"""
        if emotion_data is None:
            # 如果没有提供情感数据，则分析用户输入
            emotion_data = self.emotion_analyzer.analyze_emotion(user_input)
        emotion = emotion_data.get("emotion", "neutral")
        suggestions = emotion_data.get("suggestions", [])
        
        # 基于情感类型提供合适的回应（符合心语Prompt：3-4句话，不使用表情符号）
        fallback_responses = {
            "happy": [
                "听起来你心情很好。你的快乐让我也感到温暖。有什么特别的事情想要分享吗？",
                "看到你这么开心，我也替你高兴。这种积极的状态真好。愿意多说说是什么让你这么开心吗？",
                "你的愉快心情很有感染力。保持这样的状态很重要。想聊聊让你开心的事情吗？"
            ],
            "sad": [
                "听起来你现在很难过。这种感觉确实不好受。我在这里倾听，你愿意说说发生了什么吗？",
                "我能感受到你的伤心。每个人都会有这样的时刻，这些感受都是正常的。你并不孤单。",
                "你现在的心情一定很沉重。谢谢你愿意告诉我。想多聊聊吗？"
            ],
            "angry": [
                "听起来你很愤怒。这种情绪确实很强烈。是什么事情让你这么生气？",
                "我能感受到你的愤怒。这确实让人很不舒服。你愿意说说具体发生了什么吗？",
                "听起来有些事情真的惹恼了你。这种感觉很正常。想聊聊是什么让你这么生气吗？"
            ],
            "anxious": [
                "听起来你很焦虑。这种不安的感觉确实让人难受。你在担心什么呢？",
                "我能感受到你的紧张。焦虑的时候确实很不好受。可以跟我说说你担心的事情吗？",
                "你现在似乎很不安。这种焦虑感很沉重。想聊聊让你担心的事情吗？"
            ],
            "excited": [
                "听起来你很兴奋。这种期待的感觉真好。有什么好事要发生了吗？",
                "我能感受到你的激动。这种兴奋很有感染力。是什么让你这么期待呢？",
                "你似乎对某件事充满期待。这种感觉真棒。愿意分享一下吗？"
            ],
            "confused": [
                "听起来你感到困惑。这种迷茫的感觉确实让人不安。能说说是什么让你困惑吗？",
                "我能理解你的迷茫。有些事情确实让人摸不着头脑。想聊聊具体是什么让你困惑吗？",
                "你现在似乎有些迷茫。这种感觉很正常。愿意说说让你困惑的事情吗？"
            ],
            "frustrated": [
                "听起来你很挫败。这种感觉确实很沮丧。是什么事情让你这么受挫？",
                "我能感受到你的沮丧。这确实很让人失望。想说说发生了什么吗？",
                "你现在一定很沮丧。这种挫败感真的不好受。愿意聊聊吗？"
            ],
            "lonely": [
                "听起来你感到孤独。这种感觉确实很难受。我在这里陪着你。你想聊聊吗？",
                "我能理解你的孤独感。这种时候确实让人难过。你并不孤单，我在这里倾听。",
                "你现在一定很孤单。这种感觉很沉重。想说说你的想法吗？"
            ],
            "grateful": [
                "听起来你心怀感激。这种感恩的心很美好。是什么让你有这样的感受？",
                "我能感受到你的感恩之心。这很温暖。愿意分享是什么让你心存感激吗？",
                "你的感恩之心很动人。这种积极的情绪很珍贵。想多说说吗？"
            ],
            "neutral": [
                "今天感觉怎么样？我在这里倾听。有什么想聊的吗？",
                "我在这里陪伴你。无论你想说什么，我都愿意倾听。",
                "你现在的心情如何？想聊聊今天的事情吗？"
            ]
        }
        
        # 根据情感选择回应，如果没有对应的情感则使用建议或默认回应
        if emotion in fallback_responses and fallback_responses[emotion]:
            import random
            return random.choice(fallback_responses[emotion])
        elif suggestions:
            return suggestions[0]
        else:
            return "我在这里倾听你的心声。无论你想说什么，我都会认真倾听。你并不孤单。"
    
    def chat(self, request):
        """处理聊天请求"""
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        print(f"Chat请求: session_id={session_id}, user_id={user_id}, message={request.message[:50]}...")
        
        # 分析情感
        emotion_data = self.emotion_analyzer.analyze_emotion(request.message)
        
        # 保存用户消息到数据库
        user_message = None
        try:
            with self.db_manager as db:
                # 如果是新会话，创建会话记录
                if not request.session_id:
                    db.create_session(session_id, user_id)
                
                user_message = db.save_message(
                    session_id=session_id,
                    user_id=user_id,
                    role="user",
                    content=request.message,
                    emotion=emotion_data["emotion"],
                    emotion_intensity=emotion_data["intensity"]
                )
                
                # 保存情感分析结果
                db.save_emotion_analysis(
                    session_id=session_id,
                    user_id=user_id,
                    message_id=user_message.id,
                    emotion=emotion_data["emotion"],
                    intensity=emotion_data["intensity"],
                    keywords=emotion_data["keywords"],
                    suggestions=emotion_data["suggestions"]
                )
        except Exception as e:
            print(f"数据库操作失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 生成回应
        response_text = self.get_openai_response(request.message, user_id, session_id)
        
        # 保存助手消息到数据库
        with self.db_manager as db:
            db.save_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                emotion=emotion_data.get("emotion", "neutral")
            )
        
        # 保存对话到向量数据库（长期记忆）
        try:
            self.vector_store.add_conversation(
                session_id=session_id,
                message=request.message,
                response=response_text,
                emotion=emotion_data["emotion"]
            )
        except Exception as e:
            print("保存到向量数据库失败: {}".format(e))
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            emotion=emotion_data["emotion"],
            suggestions=emotion_data["suggestions"][:3]
        )
    
    def get_session_summary(self, session_id):
        """获取会话摘要"""
        with self.db_manager as db:
            messages = db.get_session_messages(session_id)
            if not messages:
                return {"error": "会话不存在"}
            
            # 统计情感分布
            emotion_counts = {}
            for msg in messages:
                if msg.emotion:
                    emotion_counts[msg.emotion] = emotion_counts.get(msg.emotion, 0) + 1
            
            return {
                "session_id": session_id,
                "message_count": len(messages),
                "emotion_distribution": emotion_counts,
                "created_at": messages[-1].created_at.isoformat() if messages else None,
                "updated_at": messages[0].created_at.isoformat() if messages else None
            }
    
    def get_user_emotion_trends(self, user_id):
        """获取用户情感趋势"""
        with self.db_manager as db:
            emotion_history = db.get_user_emotion_history(user_id, limit=100)
            
            if not emotion_history:
                return {"error": "没有情感数据"}
            
            # 分析情感趋势
            emotions = [e.emotion for e in emotion_history]
            intensities = [e.intensity for e in emotion_history]
            
            return {
                "user_id": user_id,
                "total_records": len(emotion_history),
                "recent_emotions": emotions[:10],
                "average_intensity": sum(intensities) / len(intensities) if intensities else 0,
                "emotion_counts": {emotion: emotions.count(emotion) for emotion in set(emotions)}
            }