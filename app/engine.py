class WorkflowGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.entry_point = None

    def add_node(self, name, func):
        """Register a function as a node."""
        self.nodes[name] = func

    def set_entry_point(self, name):
        """Where does the graph start?"""
        self.entry_point = name

    def add_edge(self, source, destination):
        """Simple transition: A -> B"""
        self.edges[source] = destination

    def add_conditional_edge(self, source, condition_func, mapping):
        """Branching logic: A -> B or A -> C based on condition"""
        self.edges[source] = (condition_func, mapping)

    def run(self, initial_state):
        """Execute the workflow loop."""
        current_node = self.entry_point
        state = initial_state
        logs = []

        while current_node:
            logs.append(f"Running node: {current_node}")
            
            # 1. Execute the node function
            node_func = self.nodes[current_node]
            state = node_func(state)

            # 2. Determine the next node
            if current_node not in self.edges:
                break # End of workflow

            transition = self.edges[current_node]

            # Check if it is a simple edge or a conditional edge
            if isinstance(transition, tuple):
                condition_func, mapping = transition
                result = condition_func(state)
                current_node = mapping.get(result)
            else:
                current_node = transition

        return state, logs