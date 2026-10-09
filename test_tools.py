"""Test each tool on its own (no LLM needed). Run: python test_tools.py"""
from tools import calculate_expression, run_python_text, search_web_text

assert calculate_expression("987654321 * 123456789") == "121932631112635269"
assert calculate_expression("2^10") == "1024"
assert calculate_expression("sqrt(144)") == "12.0"
assert calculate_expression("10/0").startswith("ERROR")
assert calculate_expression("__import__('os')").startswith("ERROR")  # unsafe input rejected
assert run_python_text("print(sum(range(101)))") == "5050"
assert run_python_text("1/0").startswith("ERROR")
assert run_python_text("while True: pass", timeout=1).startswith("ERROR: code timed out")
print("calculator + python tests passed")
print("search sample:", search_web_text("capital of Australia", 1)[:200])