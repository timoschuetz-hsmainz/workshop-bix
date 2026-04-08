from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from .tools import TOOLS


@dataclass
class OpenRouterSettings:
    api_key: str
    model: str
    base_url: str = "https://openrouter.ai/api/v1"
    app_name: str = "agentic-workshop-quickstarter"
    app_url: str = "https://example.com"


def get_settings() -> OpenRouterSettings:
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
    app_name = os.getenv("OPENROUTER_APP_NAME", "agentic-workshop-quickstarter").strip()
    app_url = os.getenv("OPENROUTER_APP_URL", "https://example.com").strip()

    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY in environment.")
    if not model:
        raise ValueError("Missing OPENROUTER_MODEL in environment.")

    return OpenRouterSettings(
        api_key=api_key,
        model=model,
        base_url=base_url,
        app_name=app_name,
        app_url=app_url,
    )


class AgentState(TypedDict):
    user_input: str
    plan: str
    response: str
    messages: Annotated[list, add_messages]


class AgentUpdate(TypedDict, total=False):
    user_input: str
    plan: str
    response: str
    messages: Annotated[list, add_messages]


def _build_llm(settings: OpenRouterSettings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=0,
        default_headers={
            "HTTP-Referer": settings.app_url,
            "X-Title": settings.app_name,
        },
    )


def planner_node(state: AgentState) -> AgentUpdate:
    llm = _build_llm(get_settings())
    planner_prompt = (
        "You are a planning assistant. Produce a short 2-4 bullet plan for solving "
        "the user request. Keep it concrete."
    )
    plan_message = llm.invoke(
        [HumanMessage(content=f"{planner_prompt}\n\nUser request: {state['user_input']}")]
    )
    plan_text = str(plan_message.content)
    return {"plan": plan_text}


def actor_node(state: AgentState) -> AgentUpdate:
    llm_with_tools = _build_llm(get_settings()).bind_tools(TOOLS)
    system = (
        "You are an assistant that can call tools when needed. "
        "Use tools for arithmetic. Keep the answer concise."
    )
    first_response: AIMessage = llm_with_tools.invoke(
        [
            HumanMessage(content=system),
            HumanMessage(content=f"Plan:\n{state['plan']}"),
            HumanMessage(content=f"User request:\n{state['user_input']}"),
        ]
    )

    tool_messages: list[ToolMessage] = []
    if first_response.tool_calls:
        tools_by_name = {tool.name: tool for tool in TOOLS}
        for call in first_response.tool_calls:
            tool_name = call["name"]
            tool = tools_by_name.get(tool_name)
            if tool is None:
                content = f"unknown_tool: {tool_name}"
            else:
                content = tool.invoke(call["args"])
            tool_messages.append(ToolMessage(content=content, tool_call_id=call["id"]))

    if tool_messages:
        final_response = llm_with_tools.invoke(
            [
                HumanMessage(content=system),
                HumanMessage(content=f"Plan:\n{state['plan']}"),
                HumanMessage(content=f"User request:\n{state['user_input']}"),
                first_response,
                *tool_messages,
            ]
        )
    else:
        final_response = first_response

    return {
        "response": str(final_response.content),
        "messages": [first_response, *tool_messages, final_response],
    }


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("actor", actor_node)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "actor")
    graph.add_edge("actor", END)
    return graph.compile()


def run_agent(user_input: str) -> dict[str, str]:
    app = build_graph()
    result = app.invoke(
        {
            "user_input": user_input,
            "plan": "",
            "response": "",
            "messages": [],
        }
    )
    return {
        "plan": result.get("plan", ""),
        "response": result.get("response", ""),
    }
