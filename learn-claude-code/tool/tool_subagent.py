import llm
from tool.definition import get_subagent_tools,get_subagent_tool_handlers
from langchain_core.messages import HumanMessage, ToolMessage

def run_subagent(prompt: str, agent_type: str = "Explore") -> str:
    sub_msgs = [HumanMessage(content=prompt)]
    response = None
    print(f"\033[31m$ subagent 启动，prompt：{prompt}\033[0m")
    client_with_tools = llm.LLM().ChatOpenAI().bind_tools(get_subagent_tools()).bind(max_tokens=8000)
    for _ in range(30):
        try:
            response = client_with_tools.invoke(sub_msgs)  
        except Exception as e:
            print(f"\033[31m$ subagent Exception：{e}\033[0m")
            return "(subagent failed)"
        sub_msgs.append(response)
        if not response.tool_calls:
            break
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"\033[31m$ subagent 工具调用：{tool_name}({tool_args})\033[0m")
            handler = get_subagent_tool_handlers().get(tool_name)
            if handler is None:
                output = f"Error: Unknown tool '{tool_name}'"
            else:
                output = handler(**tool_args)
            print(f"\033[31m$ subagent 工具结果：{output[:200]}\033[0m")
            sub_msgs.append(ToolMessage(content=output, name=tool_name, tool_call_id=tool_call["id"]))
        return response.content or "(no summary)"
        