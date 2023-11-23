import sys
import ast
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import networkx as nx
import matplotlib.pyplot as plt

def get_defined_functions(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
        tree = ast.parse(code)
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

class RuntimeFlowTracer:
    def __init__(self, variable_name, defined_functions):
        self.variable_name = variable_name
        self.defined_functions = defined_functions
        self.flow = []
        self.last_func = None
        self.last_lineno = None
        self.current_value = None
        self.line_group = []

    def trace_calls(self, frame, event, arg):
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name

        if func_name not in self.defined_functions:
            return self.trace_calls  # Skip functions not defined in the file

        if self.last_func != func_name:
            # New function call
            if self.line_group:
                self.flow.append((self.last_func, self.line_group, self.current_value))
                self.line_group = []
            self.last_func = func_name
            self.current_value = None

        if lineno not in self.line_group:
            self.line_group.append(lineno)

        self.last_lineno = lineno

        if event == 'line' and self.variable_name in frame.f_locals:
            current_value = frame.f_locals[self.variable_name]
            self.current_value = current_value

        return self.trace_calls

    def finalize_flow(self):
        if self.line_group:
            self.flow.append((self.last_func, self.line_group, self.current_value))



def start_tracing(variable_name):
    tracer = RuntimeFlowTracer(variable_name)
    sys.settrace(tracer.trace_calls)
    return tracer

def stop_tracing(tracer):
    tracer.finalize_flow()
    sys.settrace(None)
    return tracer.flow

def visualize_flow(flow):
    G = nx.DiGraph()

    # Process the flow data
    prev_node_label = None
    for func, line_group, value in flow:
        line_range = f"{line_group[0]}-{line_group[-1]}" if len(line_group) > 1 else str(line_group[0])
        node_label = f"{func} (Lines {line_range})\nVar Value: {value}"

        if node_label not in G.nodes:
            G.add_node(node_label)
            if prev_node_label:
                G.add_edge(prev_node_label, node_label)
            prev_node_label = node_label

    # Layout and drawing
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos)
    plt.show()

def execute_and_trace(file_path, variable_name, tracer):
    with open(file_path, 'r') as file:
        code = file.read()
        exec_globals = {}
        exec_globals['__name__'] = '__main__'  # Set __name__ to emulate a main execution environment
        sys.settrace(tracer.trace_calls)  # Set the trace function
        exec(code, exec_globals)  # Execute the code
        sys.settrace(None)  # Stop tracing after execution

def main():
    file_path = filedialog.askopenfilename()
    if file_path:
        variable_name = simpledialog.askstring("Input", "Enter the variable name to trace:")
        defined_functions = get_defined_functions(file_path)
        if variable_name:
            tracer = RuntimeFlowTracer(variable_name, defined_functions)
            execute_and_trace(file_path, variable_name, tracer)
            flow = stop_tracing(tracer)
            visualize_flow(flow)

if __name__ == "__main__":
    main()
