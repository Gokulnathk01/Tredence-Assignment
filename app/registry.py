def check_complexity(code_str):
    """Mock tool: counts length of code."""
    return len(code_str)

def lint_code(code_str):
    """Mock tool: returns random issues."""
    if "error" in code_str:
        return ["Syntax Error found"]
    return []

# The Registry
TOOL_REGISTRY = {
    "check_complexity": check_complexity,
    "lint_code": lint_code
}