import networkx as nx
import matplotlib.pyplot as plt
import ast
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

def parse_python_file(file_path):
    with open(file_path, "r") as source:
        code = source.read()
        return ast.parse(code)
    
class VariableFlowAnalyzer(ast.NodeVisitor):
    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.flow = []
        self.current_function = None
        self.occurrence_counter = 0

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None

    def process_variable_occurrence(self, lineno):
        # Add a placeholder (e.g., None) for the conditional type
        unique_occurrence = (self.current_function, lineno, self.occurrence_counter, None)
        self.flow.append(unique_occurrence)
        self.occurrence_counter += 1

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name) and node.targets[0].id == self.variable_name:
            self.process_variable_occurrence(node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node):
        for arg in node.args:
            if isinstance(arg, ast.Name) and arg.id == self.variable_name:
                self.process_variable_occurrence(node.lineno)
        self.generic_visit(node)

    def visit_If(self, node):
    # Process the 'if' part
        self.process_conditional_occurrence(node.lineno, 'if')
        self.generic_visit(node.test)  # Visit the test expression of the 'if' statement

        # Process the body of the 'if'
        for n in node.body:
            self.visit(n)  # Visit each node in the body of the 'if'

        # Process 'elif' and 'else' parts
        for orelse in node.orelse:
            if isinstance(orelse, ast.If):
                self.process_conditional_occurrence(orelse.lineno, 'elif')
                self.generic_visit(orelse.test)
                for n in orelse.body:
                    self.visit(n)
            elif isinstance(orelse, ast.Expr):
                self.visit(orelse)
            else:
                # Handle other types of nodes in the 'else' part
                for n in getattr(orelse, 'body', []):
                    self.visit(n)

    def process_conditional_occurrence(self, lineno, conditional_type):
        unique_occurrence = (self.current_function, lineno, self.occurrence_counter, conditional_type)
        self.flow.append(unique_occurrence)
        self.occurrence_counter += 1
    

def get_current_function(lineno, code):
    """Parse the code and find the function name for the given line number."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            if start_line <= lineno <= end_line:
                return node.name
    return "Global Scope"

def visualize_flow(flow, current_function):
    G = nx.DiGraph()

    # Function map to track occurrences
    func_map = {}
    for func, lineno, _, _ in flow:
        if func not in func_map:
            func_map[func] = []
        func_map[func].append(lineno)

    # Create node label map for the graph
    node_label_map = {func: f"{func}\nLines: {', '.join(map(str, lines))}" for func, lines in func_map.items()}

    # Add nodes to the graph
    for func, node_label in node_label_map.items():
        G.add_node(node_label)

    # Add edges between nodes based on the flow
    prev_node_label = None
    for func, lineno, _, conditional_type in flow:
        node_label = node_label_map[func]

        # Differentiate edges for conditional flows
        if conditional_type in ['if', 'elif', 'else']:
            edge_style = 'dotted'
        else:
            edge_style = 'solid'

        if prev_node_label is not None and prev_node_label != node_label:
            G.add_edge(prev_node_label, node_label, style=edge_style)
        prev_node_label = node_label

    # Determine the colors for each node
    node_colors = [get_node_color(func, current_function, func_map) for func, _ in node_label_map.items()]

    # Layout and drawing
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors)
    nx.draw_networkx_labels(G, pos)

    # Draw edges with respective styles
    for u, v, attr in G.edges(data=True):
        style = attr.get('style', 'solid')
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], style=style, arrows=True)

    plt.show()


def get_node_color(func, current_function, func_map):
    if func == current_function:
        return 'green'  # Current function
    elif list(func_map).index(func) < list(func_map).index(current_function):
        return 'red'  # Previous functions
    else:
        return 'blue'  # Future functions


def analyze_highlighted_variable():
    try:
        if not text.tag_ranges(tk.SEL):
            print("Please select a variable name in the text.")
            return
        print("OK")
        start_index = text.index(tk.SEL_FIRST)
        print(start_index)
        end_index = text.index(tk.SEL_LAST)
        print(end_index)
        variable_name = text.get(start_index, end_index)
        print(variable_name)
        lineno = int(start_index.split('.')[0])

        # Determine the current function
        current_function = get_current_function(lineno, code)

        # Check if the selected text corresponds to a valid variable name
        if not is_valid_variable_name(variable_name):
            print(f"'{variable_name}' is not a valid variable name.")
            return

        analyzer = VariableFlowAnalyzer(variable_name)
        analyzer.visit(ast.parse(code))
        visualize_flow(analyzer.flow, current_function)
    except Exception as e:
        print("Error:", e)

def is_valid_variable_name(variable_name):
    try:
        # Attempt to parse the variable name as an ast.Name
        ast.parse(variable_name, mode='eval')
        return True
    except SyntaxError:
        return False


def select_variable_and_visualize(file_path):
    global text, code
    root = tk.Tk()
    text = tk.Text(root)
    text.pack(expand=True, fill="both")

    analyze_button = tk.Button(root, text="Test Button", command=analyze_highlighted_variable)
    analyze_button.pack()

    with open(file_path, 'r') as file:
        code = file.read()
        text.insert('1.0', code)

    root.mainloop()

def main():
    file_path = filedialog.askopenfilename()
    if file_path:
        select_variable_and_visualize(file_path)

if __name__ == "__main__":
    main()
