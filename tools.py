"""Tools the agent can call. Each does something an LLM cannot do reliably alone.

Every tool catches its own errors and returns them as text, so a failure
becomes information the agent can react to instead of crashing the run.
"""
import ast
import math
import operator
import subprocess
import sys

from langchain_core.tools import tool

# ---------- 1. Calculator (exact arithmetic) ----------
_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {"sqrt": math.sqrt, "log": math.log, "log10": math.log10,
          "sin": math.sin, "cos": math.cos, "tan": math.tan,
          "abs": abs, "round": round, "factorial": math.factorial}
_CONSTS = {"pi": math.pi, "e": math.e}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10_000:
            raise ValueError("exponent too large")
        return _BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCS):
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("unsupported expression")


def calculate_expression(expression: str) -> str:
    """Plain function (testable without LangChain)."""
    try:
        result = _eval(ast.parse(expression.strip().replace("^", "**"), mode="eval").body)
        return str(result)
    except ZeroDivisionError:
        return "ERROR: division by zero."
    except Exception as exc:
        return f"ERROR: could not evaluate '{expression}' ({exc}). Check the syntax."


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression EXACTLY, e.g. '987654321 * 123456789' or
    'sqrt(2) * 5 / 3'. Supports + - * / // % ** ^, parentheses, sqrt, log,
    sin, cos, tan, factorial, pi, e. Use this for ANY arithmetic involving
    large numbers or many digits; do not do such math in your head."""
    return calculate_expression(expression)


# ---------- 2. Web search (real-time information) ----------
def search_web_text(query: str, max_results: int = 5) -> str:
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
    except Exception as exc:
        return f"ERROR: search failed ({exc}). Try again or rephrase the query."
    if not results:
        return "NO RESULTS: the search returned nothing. Try different keywords."
    return "\n\n".join(
        f"[{i}] {r.get('title', '')}\n{r.get('body', '')}\n({r.get('href', '')})"
        for i, r in enumerate(results, 1)
    )


@tool
def web_search(query: str) -> str:
    """Search the web for CURRENT or factual information the model may not
    know (recent news, today's figures, populations, prices, who holds an
    office now). Returns the top results as text snippets with URLs. Do not
    use for stable general knowledge or for math."""
    return search_web_text(query)


# ---------- 3. Python code execution ----------
def run_python_text(code: str, timeout: int = 10) -> str:
    try:
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"ERROR: code timed out after {timeout}s."
    except Exception as exc:
        return f"ERROR: could not run code ({exc})."
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0:
        return f"ERROR (exit {proc.returncode}):\n{err[-1500:]}"
    return (out or "(no output - use print() to see results)")[:3000]


@tool
def python_repl(code: str) -> str:
    """Execute Python code and return what it prints. Use it for anything that
    needs real computation or logic: loops, sorting, primes, date math, data
    processing. Always print() the final result. Runs in a fresh process each
    call with a 10 second limit (no state is kept between calls)."""
    return run_python_text(code)


ALL_TOOLS = [calculator, web_search, python_repl]