from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid

# FIXED IMPORTS: Removed "app." prefix
from engine import WorkflowGraph
from workflows import create_code_review_graph

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
    
    # FIXED: Ensure 'logs' list exists in state to prevent KeyError in nodes
    if "logs" not in request.initial_state:
        request.initial_state["logs"] = []

    final_state, logs = graph.run(request.initial_state)
    
    run_id = str(uuid.uuid4())
    RUNS[run_id] = {"state": final_state, "logs": logs}
    
    return {
        "run_id": run_id,
        "final_state": final_state, 
        "logs": logs
    }

@app.get("/graph/state/{run_id}")
def get_state(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS[run_id]