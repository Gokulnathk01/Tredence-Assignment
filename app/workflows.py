from registry import TOOL_REGISTRY



def extract_functions_node(state):
    """Step 1: Extract functions (Mocking by splitting text)."""
    code = state.get("code", "")
 
    functions = [line for line in code.split("\n") if line.strip().startswith("def ")]
    state["extracted_functions"] = functions
    state["logs"].append(f"Extracted {len(functions)} functions.")
    return state

def check_complexity_node(state):
    """Step 2: Check complexity (Mocking by length)."""
    code = state.get("code", "")
    
    if "quality_score" not in state:
        state["quality_score"] = 40  
    
    state["logs"].append(f"Checked complexity. Current Score: {state['quality_score']}")
    return state

def detect_issues_node(state):
    """Step 3: Detect basic issues."""
    issues = []
    if "bad_code" in state.get("code", ""):
        issues.append("Found usage of 'bad_code'")
    
    state["issues"] = issues
    state["logs"].append(f"Issues found: {len(issues)}")
    return state

def suggest_improvements_node(state):
    """Step 4: Suggest improvements (Refine the code)."""
  
    state["code"] += "\n# Optimized by Agent"
    state["quality_score"] += 20  
    state["logs"].append("Applied improvements. Score increased.")
    return state

def check_quality_gate(state):
    """Step 5: Loop until quality_score >= threshold."""
    score = state.get("quality_score", 0)
    
   
    if score >= 80:
        return "pass"
    
    
    if len(state["logs"]) > 20: 
        return "pass"
        
    return "fail"



def create_code_review_graph(graph_engine):
    
    graph_engine.add_node("extract", extract_functions_node)
    graph_engine.add_node("complexity", check_complexity_node)
    graph_engine.add_node("issues", detect_issues_node)
    graph_engine.add_node("improve", suggest_improvements_node)

   
    graph_engine.set_entry_point("extract")

   
    graph_engine.add_edge("extract", "complexity")
    
    
    graph_engine.add_edge("complexity", "issues")
    
   
    graph_engine.add_conditional_edge(
        "issues", 
        check_quality_gate, 
        {
            "fail": "improve", 
            "pass": None  
        }
    )

   
    graph_engine.add_edge("improve", "complexity")

    return graph_engine