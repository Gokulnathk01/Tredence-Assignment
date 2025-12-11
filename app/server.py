import uuid
from typing import Dict, Any, List, Optional, Callable
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# PART 1: THE ENGINE (No changes needed)

class WorkflowGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.entry_point = None

    def add_node(self, name, func):
        self.nodes[name] = func

    def set_entry_point(self, name):
        self.entry_point = name

    def add_edge(self, source, destination):
        self.edges[source] = destination

    def add_conditional_edge(self, source, condition_func, mapping):
        self.edges[source] = (condition_func, mapping)

    def run(self, initial_state):
        current_node = self.entry_point
        state = initial_state
        logs = []

        while current_node:
            logs.append(f"Running node: {current_node}")
            
            node_func = self.nodes[current_node]
            state = node_func(state)

            if current_node not in self.edges:
                break 

            transition = self.edges[current_node]

            if isinstance(transition, tuple):
                condition_func, mapping = transition
                result = condition_func(state)
                current_node = mapping.get(result)
            else:
                current_node = transition

        return state, logs


# PART 2: THE WORKFLOW NODES & LOGIC


def extract_functions_node(state):
    code = state.get("code", "")
    functions = [line for line in code.split("\n") if line.strip().startswith("def ")]
    state["extracted_functions"] = functions
    state["logs"].append(f"Extracted {len(functions)} functions.")
    return state

def check_complexity_node(state):
    if "quality_score" not in state:
        state["quality_score"] = 40  
    state["logs"].append(f"Checked complexity. Current Score: {state['quality_score']}")
    return state

def detect_issues_node(state):
    issues = []
    if "bad_code" in state.get("code", ""):
        issues.append("Found usage of 'bad_code'")
    state["issues"] = issues
    state["logs"].append(f"Issues found: {len(issues)}")
    return state

def suggest_improvements_node(state):
    state["code"] += "\n# Optimized by Agent"
    state["quality_score"] += 20  
    state["logs"].append("Applied improvements. Score increased.")
    return state

def check_quality_gate(state):
    score = state.get("quality_score", 0)
    if score >= 80: return "pass"
    if len(state["logs"]) > 20: return "pass" 
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
        {"fail": "improve", "pass": None}
    )
    graph_engine.add_edge("improve", "complexity")
    return graph_engine


# PART 3: THE API SERVER (FastAPI)


app = FastAPI()

GRAPHS = {}
RUNS = {}

class CreateGraphRequest(BaseModel):
    workflow_type: str 

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

@app.post("/graph/create")
def create_graph(request: CreateGraphRequest):
    graph_id = str(uuid.uuid4())
    graph = WorkflowGraph()
    if request.workflow_type == "code_review":
        create_code_review_graph(graph)
    GRAPHS[graph_id] = graph
    return {"graph_id": graph_id}

@app.post("/graph/run")
def run_graph(request: RunGraphRequest):
    graph = GRAPHS.get(request.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    

    if "logs" not in request.initial_state:
        request.initial_state["logs"] = []

    final_state, logs = graph.run(request.initial_state)
    
    run_id = str(uuid.uuid4())
    RUNS[run_id] = {"state": final_state, "logs": logs}
    
    return {"run_id": run_id, "final_state": final_state, "logs": logs}

@app.get("/")
def read_root():
    return {"message": "Server is running correctly!"}