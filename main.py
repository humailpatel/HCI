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

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None

    def process_variable_occurrence(self, lineno, conditional=False):
        unique_occurrence = (self.current_function, lineno, conditional)
        self.flow.append(unique_occurrence)

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name) and node.targets[0].id == self.variable_name:
            self.process_variable_occurrence(node.lineno)
        self.generic_visit(node)

    def visit_If(self, node):
        self.generic_visit(node)
        test_result = None

        if isinstance(node.test, ast.Compare):
            left = node.test.left.id if isinstance(node.test.left, ast.Name) else None
            right = node.test.comparators[0].id if isinstance(node.test.comparators[0], ast.Name) else None

            if left == self.variable_name or right == self.variable_name:
                test_result = True
            else:
                test_result = False

        for stmt in node.body:
            if test_result is None or test_result:
                self.visit(stmt)

        for stmt in node.orelse:
            if test_result is None or not test_result:
                self.visit(stmt)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            called_function = node.func.id
            conditional = self.variable_name in [arg.id for arg in node.args if isinstance(arg, ast.Name)]
            self.process_variable_occurrence(node.lineno, conditional)
        self.generic_visit(node)

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
    for func, lineno, _ in flow:
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
    for func, lineno, _ in flow:
        node_label = node_label_map[func]
        if prev_node_label is not None and prev_node_label != node_label:
            G.add_edge(prev_node_label, node_label)
        prev_node_label = node_label

    # Determine the colors for each node
    node_colors = []
    for func, node_label in node_label_map.items():
        if func == current_function:
            node_colors.append('green')  # Current function
        elif list(func_map.keys()).index(func) < list(func_map.keys()).index(current_function):
            node_colors.append('red')  # Previous functions
        else:
            node_colors.append('blue')  # Future functions

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, arrows=True, node_color=node_colors)
    plt.show()

def is_valid_variable_name(variable_name):
    try:
        # Attempt to parse the variable name as an ast.Name
        ast.parse(variable_name, mode='eval')
        return True
    except SyntaxError:
        return False

def analyze_highlighted_variable():
    try:
        if not text.tag_ranges(tk.SEL):
            print("Please select a variable name in the text.")
            return

        start_index = text.index(tk.SEL_FIRST)
        end_index = text.index(tk.SEL_LAST)
        variable_name = text.get(start_index, end_index)
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

def select_variable_and_visualize(file_path):
    global text, code
    root = tk.Tk()
    text = tk.Text(root)
    text.pack(expand=True, fill='both')

    # Add a button to analyze the highlighted text
    analyze_button = tk.Button(root, text="Analyze Variable Flow", command=analyze_highlighted_variable)
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
