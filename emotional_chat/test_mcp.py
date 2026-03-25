from backend.modules.agent.protocol.mcp import MCPProtocol, create_mcp_protocol_with_context, MCPToolCall, MCPToolResponse, get_mcp_logger

# 使用示例
if __name__ == "__main__":
    # 创建MCP协议处理器（不带上下文服务）
    protocol = MCPProtocol()
    
    # 创建带上下文服务的MCP协议处理器
    protocol_with_context = create_mcp_protocol_with_context()
    
    # 示例1：创建用户输入消息（静态方法，不自动填充上下文）
    user_msg = protocol.create_user_input(
        content="我最近心情很不好，感觉很焦虑",
        emotion_state={"emotion": "焦虑", "intensity": 7.5}
    )
    print("用户输入消息（静态方法）：")
    print(user_msg.to_json())
    print("\n" + "="*60 + "\n")
    
    # 示例1b：创建用户输入消息（自动填充上下文）
    # 注意：这是异步方法，需要在实际使用时用 await
    # user_msg_with_context = await protocol_with_context.create_user_input_with_context(
    #     content="我最近心情很不好，感觉很焦虑",
    #     user_id="user_123",
    #     session_id="session_456",
    #     emotion="焦虑",
    #     emotion_intensity=7.5
    # )
    # print("用户输入消息（自动填充上下文）：")
    # print(user_msg_with_context.to_json())
    # print("\n" + "="*60 + "\n")
    
    # 示例2：创建Planner输出消息
    tool_call = MCPToolCall(
        tool_name="search_memory",
        parameters={"query": "焦虑", "user_id": "user_123"}
    )
    planner_msg = protocol.create_planner_output(
        content="识别到情感支持需求，需要检索相关记忆",
        task_goal={"goal_type": "emotional_support", "complexity": "medium"},
        tool_calls=[tool_call]
    )
    print("Planner输出消息：")
    print(planner_msg)
    print("\n" + "="*60 + "\n")

    # 示例3：创建工具响应消息
    tool_response = MCPToolResponse(
        tool_id=tool_call.tool_id,
        tool_name="search_memory",
        success=True,
        result={"count": 3, "memories": []}
    )
    tool_response_msg = protocol.create_tool_response(
        tool_responses=[tool_response]
    )
    print("工具响应消息：")
    print(tool_response_msg)
    print("\n" + "="*60 + "\n")
    
    # 示例4：使用日志记录器
    logger = get_mcp_logger()
    logger.log(user_msg)
    logger.log(planner_msg)
    logger.log(tool_response_msg)
    
    print("日志记录：")
    print(f"共记录了 {len(logger.get_logs())} 条消息")
