import uuid
from typing import Dict
from datetime import datetime
import os
import dashvector
import dashscope
from dashscope import TextEmbedding

class VectorStore:
    def __init__(self):
        """
        初始化向量数据库管理器
        """
        # 从环境变量获取API密钥
        api_key = os.getenv("ALIYUN_DASH_VECTOR_API_KEY")
        if not api_key:
            raise ValueError("ALIYUN_DASH_VECTOR_API_KEY environment variable not set")
        
        # 初始化DashVector客户端
        self.client = dashvector.Client(
            api_key=api_key,
            endpoint="vrs-cn-wte4mpdcy0002q.dashvector.cn-beijing.aliyuncs.com"
        )
        
        # 验证连接并检查必要的collection
        self._validate_collections()
    
    def _validate_collections(self):
        """
        验证必要的collection是否存在
        """
        try:
            # 获取所有collection
            collections = self.client.list()
            
            if not collections or len(collections.output) == 0:
                raise Exception("Failed to list collections. Please check your API key and endpoint.")
            
            # 检查必要的collection是否存在
            required_collections = ["conversation", "knowledge", "emotion"]
            
            missing_collections = []
            for col_name in required_collections:
                if col_name not in collections.output:
                    missing_collections.append(col_name)
            
            if missing_collections:
                raise Exception(f"Missing required collections: {', '.join(missing_collections)}. Please create them first.")
            
            print("✓ All required collections exist.")
            
        except Exception as e:
            print(f"Error validating collections: {e}")
            raise
    
    def generate_embeddings(self, text):
        """
        生成文本的向量表示
        
        Args:
            text: 文本字符串或文本列表
            
        Returns:
            list: 向量表示，或向量列表（如果输入是文本列表）
        """
        # 从环境变量获取API密钥
        api_key = os.getenv("ALIYUN_TONGYI_QWEN_API_KEY")
        if not api_key:
            raise ValueError("ALIYUN_TONGYI_QWEN_API_KEY environment variable not set")
        
        dashscope.api_key = api_key
        
        # 调用TextEmbedding生成向量
        rsp = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v3,
            dimension=1024,
            input=text
        )
        
        # 提取向量
        embeddings = [record['embedding'] for record in rsp.output['embeddings']]
        return embeddings if isinstance(text, list) else embeddings[0]
    
    def _add_doc(self, collection_name, vector, fields: Dict = None):
        """
        添加对话到collection
        
        Args:
            vector: 向量表示
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if fields is None:
                fields = {}
            if "create_time" not in fields:
                fields["create_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            collection = self.client.get(collection_name)
            result = collection.insert(
                dashvector.Doc(
                    vector=vector,
                    fields=fields
                )
            )
            return result
        except Exception as e:
            print(f"Error adding to collection: {e}")
            return False
        
    def _search_doc(self, collection_name, vector, topk=5, filter=""):
        """
        在conversation collection中相似检索
        
        Args:
            collection_name: 集合名称
            vector: 查询向量
            topk: 返回结果数量
            filter: 过滤条件
            
        Returns:
            list: 检索结果
        """
        try:
            collection = self.client.get(collection_name)
            results = collection.query(
                vector=vector,
                topk=topk,
                filter=filter
            )
            return results
        except Exception as e:
            print(f"Error searching conversation: {e}")
            return []
    
    # Conversation Collection 操作
    def add_conversation(self, session_id: str, message: str, response: str, emotion: str = None):
        """
        添加对话到conversation collection
        
        Args:
            session_id: 会话ID
            message: 用户输入
            response: 助手回复
            emotion: 情感标签（可选）
            
        Returns:
            bool: 是否添加成功
        """
        conversation_text = f"用户: {message}\n助手: {response}"
        if emotion:
            conversation_text += f"\n情感: {emotion}"

        try:
            embedding = self.generate_embeddings(conversation_text)
            result = self._add_doc("conversation", embedding, fields={
                "session_id": session_id,
                "message": conversation_text,
                "emotion": emotion or "neutral",
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return result
        except Exception as e:
            print(f"Error adding to conversation: {e}")
            return False
    
    def search_similar_conversation(self, query: str, session_id: str = None, topk: int = 5):
        """
        在conversation collection中相似检索
        
        Args:
            query: 查询向量
            session_id: 会话ID（可选）
            topk: 返回结果数量

        Returns:
            list: 检索结果
        """
        try:
            embedding = self.generate_embeddings(query)
            filter = f"session_id = '{session_id}'" if session_id else ""
            print(f"Filter: {filter}")
            results = self._search_doc("conversation", embedding, topk, filter)
            print(f"Search results: {results}")
            return results
        except Exception as e:
            print(f"Error searching conversation: {e}")
            return []
    
    def get_conversation(self, session_id: str, limit: int = 10):
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 返回结果数量
            
        Returns:
            list: 会话历史记录
        """
        try:
            filter = f"session_id ='{session_id}'"
            results = self._search_doc("conversation", None, limit, filter)
            return results
        except Exception as e:
            print(f"Error searching conversation: {e}")
            return []
    
    # Knowledge Collection 操作
    def add_knowledge(self, text: str, category: str = "general", fields: Dict = None):
        """
        添加知识到knowledge collection
        
        Args:
            text: 知识文本
            category: 知识类别（可选）
            fields: 其他字段（可选）
            
        Returns:
            bool: 是否添加成功
        """
        try:
            embedding = self.generate_embeddings(text)
            result = self._add_doc("knowledge", embedding, fields={
                "category": category,
                **(fields or {})
            })
            
            return result
        except Exception as e:
            print(f"Error adding to knowledge: {e}")
            return False
    
    def search_similar_knowledge(self, query: str, category: str = None, topk: int = 5):
        """
        在knowledge collection中相似检索
        
        Args:
            query: 查询文本
            category: 知识类别（可选）
            topk: 返回结果数量
            
        Returns:
            list: 检索结果
        """
        filter = f"category = '{category}'" if category else ""

        try:
            embedding = self.generate_embeddings(query)
            results = self._search_doc("knowledge", embedding, topk, filter)

            return results
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
    
    # Emotion Collection 操作
    def add_emotion(self, text: str, emotion: str, intensity: float):
        """
        添加情感到emotion collection
        
        Args:
            text: 情感文本
            emotion: 情感类别
            intensity: 情感强度（0-1之间的浮点数）
            
        Returns:
            bool: 是否添加成功
        """
        try:
            embedding = self.generate_embeddings(text)
            result = self._add_doc("emotion", embedding, fields={
                "emotion": emotion,
                "intensity": intensity
            })
            
            return result
        except Exception as e:
            print(f"Error adding to emotion: {e}")
            return False
    
    def search_similar_emotion(self, query: str, emotion: str = None, topk: int = 3):
        """
        在emotion collection中相似检索
        
        Args:
            query: 查询文本
            emotion: 情感类别（可选）
            topk: 返回结果数量
            
        Returns:
            list: 检索结果
        """
        try:
            filter = f"emotion = '{emotion}'" if emotion else ""
            embedding = self.generate_embeddings(query)
            results = self._search_doc("emotion", embedding, topk, filter)
    
            return results
        except Exception as e:
            print(f"Error searching emotion: {e}")
            return []

    # user_memories Collection 操作
    def add_user_memories(self, text: str, fields: Dict = None):
        """ 
        添加用户记忆到user_memories collection
        
        Args:
            text: 记忆文本
            fields: 其他字段（可选）
            
        Returns:
            bool: 是否添加成功
        """
        try:
            embedding = self.generate_embeddings(text)
            result = self._add_doc("user_memories", embedding, fields=fields)
            
            return result
        except Exception as e:
            print(f"Error adding to user_memories: {e}")
            return False
        
    
    def search_similar_user_memories(self, query: str, filter: Dict = None, topk: int = 3):
        """
        在user_memories collection中相似检索
        
        Args:
            query: 查询文本
            filter: 过滤条件（可选）
            topk: 返回结果数量
            
        Returns:
            list: 检索结果
        """
        try:
            embedding = self.generate_embeddings(query)
            results = self._search_doc("user_memories", embedding, topk, filter)
            return results

            return results
        except Exception as e:
            print(f"Error searching user_memories: {e}")
            return []

    def delete_user_memories(self, id: str):
        """
        在user_memories collection中删除指定记忆
        
        Args:
            id: 记忆ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            results = self.client.get("user_memories").delete(id)
            return results
        except Exception as e:
            print(f"Error deleting user_memories: {e}")
            return False
