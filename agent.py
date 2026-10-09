"""LangChain tool-using agent with visible reasoning/tool steps.

Usage:
    python agent.py "your question"
    python agent.py --demo        # runs the 5 test scenarios, saves example_runs.md
"""
import io
import os
import sys
from contextlib import redirect_stdout

from dotenv import load_dotenv
from langchain.agents import create_agent  # LangChain 1.x agent, built on LangGraph
from langchain.chat_models import init_chat_model

from tools import ALL_TOOLS

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant with tools: calculator, web_search, python_repl.
Rules:
- If you can answer reliably from your own knowledge, answer directly and call NO tools.
- Use calculator for arithmetic with big numbers, web_search for current/real-time facts,
  python_repl for code or logic.
- BEFORE every tool call, write one short sentence saying WHY you are using that tool.
- If a tool returns an ERROR or NO RESULTS, do not give up: retry with a fix, try another
  tool, or clearly tell the user what failed.
- Never invent numbers you were supposed to look up or compute."""


def build_agent():
    model = init_chat_model(os.getenv("MODEL", "anthropic:claude-sonnet-5-5"))
    return create_agent(model, ALL_TOOLS, system_prompt=SYSTEM_PROMPT)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")


def run(agent, question: str) -> str:
    """Stream the agent and print every thought, tool call and tool result."""
    print(f"\n{'=' * 70}\nQUESTION: {question}\n{'=' * 70}")
    final, tool_calls = "", 0
    try:
        for step in agent.stream({"messages": [("user", question)]},
                                 stream_mode="values", config={"recursion_limit": 25}):
            msg = step["messages"][-1]
            kind = type(msg).__name__
            if kind == "AIMessage":
                if _text(msg.content).strip():
                    label = "FINAL ANSWER" if not msg.tool_calls else "REASONING"
                    print(f"\n[{label}] {_text(msg.content).strip()}")
                for call in msg.tool_calls:
                    tool_calls += 1
                    print(f"[TOOL CALL #{tool_calls}] {call['name']}({call['args']})")
                if not msg.tool_calls:
                    final = _text(msg.content).strip()
            elif kind == "ToolMessage":
                print(f"[TOOL RESULT] {msg.name}: {_text(msg.content)[:600]}")
    except Exception as exc:  # agent-level safety net: never crash the program
        final = f"Agent run failed gracefully: {exc}"
        print(f"\n[AGENT ERROR] {final}")
    print(f"\n--- tool calls made: {tool_calls} ---")
    return final


DEMO_QUESTIONS = [
    ("1. No tool needed", "What is the capital of France?"),
    ("2. Single tool (calculator)", "What is 987654321 * 123456789?"),
    ("3. Multi-step (search x2 + calculator)",
     "Search for the current populations of Japan and Canada, then calculate how many "
     "times larger Japan's population is than Canada's."),
    ("4. Code execution", "Use code to list all prime numbers between 100 and 150 and tell me how many there are."),
    ("5. Tool failure handling",
     "Use the calculator to compute 10 / 0, then search the web for 'zzqxv kjwpl mnbvc 99182' "
     "and tell me what happened with each."),
]


def demo(agent):
    sections = []
    for title, q in DEMO_QUESTIONS:
        buf = io.StringIO()
        with redirect_stdout(buf):
            run(agent, q)
        text = buf.getvalue()
        print(f"### {title}{text}")
        sections.append(f"### {title}\n```text{text}```\n")
    with open("example_runs.md", "w", encoding="utf-8") as f:
        f.write("# Example runs\n\n" + "\n".join(sections))
    print("\nSaved real logs to example_runs.md - paste them into your README.")


if __name__ == "__main__":
    agent = build_agent()
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo(agent)
    elif len(sys.argv) > 1:
        run(agent, " ".join(sys.argv[1:]))
    else:
        print("Usage: python agent.py \"question\"   |   python agent.py --demo")