from backend.models import ChatRequest
from backend.modules.llm.core.llm_core import SimpleEmotionalChatEngine


a = SimpleEmotionalChatEngine()
request = ChatRequest(
    session_id='aedb87cf-bd03-4d16-a935-e5406840df9a',
    user_id='1',
    message="我有点开心",
    long_memory="暂无",
    history="暂无"
)
result = a.chat(request)
print(result)


