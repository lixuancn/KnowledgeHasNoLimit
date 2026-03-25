import json
from backend.vector_store import VectorStore



# 测试向量存储管理器
vector_store = VectorStore()
print("Vector store initialized successfully.")

# 测试向量化功能
test_text = "这是一个测试文本"
embedding = vector_store.generate_embeddings(test_text)
print(f"Generated embedding length: {len(embedding)}")
print(f"First 5 elements: {embedding[:5]}")

# 测试添加到conversation
add_result = vector_store.add_conversation("sessionid_2", "我最近压力好大", "抱抱你")
print(f"Add to conversation result: {add_result}")    
# 测试检索conversation
search_result = vector_store.search_similar_conversation("压力")
print(f"Search conversation result: {search_result}")

search_result = vector_store.get_conversation("sessionid_2")
print(f"Get conversation result: {search_result}")

# 测试添加到knowledge
add_result = vector_store.add_knowledge("这是一个关于压力的知识", category="压力")
print(f"Add to knowledge result: {add_result}")

# 测试检索knowledge
search_result = vector_store.search_similar_knowledge("压力", category="压力")
print(f"Search knowledge result: {search_result}")

# 测试添加到emotion
add_result = vector_store.add_emotion("我最近很焦虑", "anxious", 0.8)
print(f"Add to emotion result: {add_result}")

# 测试检索emotion
search_result = vector_store.search_similar_emotion("焦虑", emotion="anxious")
print(f"Search emotion result: {search_result}")