# LangChain Tool-Using Agent

An agent (LangChain 1.x `create_agent`, built on LangGraph) that decides on its own
when to call tools, and logs every reasoning step, tool call and tool result.

## Tools
| Tool | Why the LLM can't do this alone |
|---|---|
| `calculator` | Exact arithmetic on large numbers (safe AST evaluator, no `eval`) |
| `web_search` | Real-time information (DuckDuckGo via `ddgs`, no API key) |
| `python_repl` | Actually executes code (subprocess, 10s timeout) |

## How each requirement is met
- **2+ real tools:** three tools in `tools.py`, each tested alone in `test_tools.py`.
- **Tool vs. direct answer:** tool descriptions and the system prompt tell the model to
  answer directly when it can. See runs 1 vs 2 below.
- **Multi-step:** run 3 searches twice, then calculates.
- **Visible steps:** `run()` in `agent.py` prints `[REASONING]`, `[TOOL CALL]`,
  `[TOOL RESULT]`, `[FINAL ANSWER]`.
- **Failure handling:** tools return `ERROR:` / `NO RESULTS:` text instead of raising,
  and the whole run is wrapped in try/except. See run 5.

## Setup
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env     # add your ANTHROPIC_API_KEY
    python test_tools.py
    python agent.py --demo
    python agent.py "your own question"

## Example runs
(PASTE the full contents of example_runs.md here)