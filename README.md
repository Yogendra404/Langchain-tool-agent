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

# Example runs

### 1. No tool needed
```text
======================================================================
QUESTION: What is the capital of France?
======================================================================

[AGENT ERROR] Agent run failed gracefully: Error calling model 'gemini-flash-latest' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 19h56m12.156889892s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.8-flash'}, 'quotaValue': '20'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '71772s'}]}}

--- tool calls made: 0 ---
```

### 2. Single tool (calculator)
```text
======================================================================
QUESTION: What is 987654321 * 123456789?
======================================================================

[AGENT ERROR] Agent run failed gracefully: Error calling model 'gemini-flash-latest' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 19h55m27.095033526s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.8-flash'}, 'quotaValue': '20'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '71727s'}]}}

--- tool calls made: 0 ---
```

### 3. Multi-step (search x2 + calculator)
```text
======================================================================
QUESTION: Search for the current populations of Japan and Canada, then calculate how many times larger Japan's population is than Canada's.
======================================================================

[AGENT ERROR] Agent run failed gracefully: Error calling model 'gemini-flash-latest' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 19h54m48.164427002s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.8-flash'}, 'quotaValue': '20'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '71688s'}]}}

--- tool calls made: 0 ---
```

### 4. Code execution
```text
======================================================================
QUESTION: Use code to list all prime numbers between 100 and 150 and tell me how many there are.
======================================================================

[AGENT ERROR] Agent run failed gracefully: Error calling model 'gemini-flash-latest' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 19h54m8.565887164s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.8-flash'}, 'quotaValue': '20'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '71648s'}]}}

--- tool calls made: 0 ---
```

### 5. Tool failure handling
```text
======================================================================
QUESTION: Use the calculator to compute 10 / 0, then search the web for 'zzqxv kjwpl mnbvc 99182' and tell me what happened with each.
======================================================================

[AGENT ERROR] Agent run failed gracefully: Error calling model 'gemini-flash-latest' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 19h53m30.791742959s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.8-flash'}, 'quotaValue': '20'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '71610s'}]}}

--- tool calls made: 0 ---
```

