import sys
import ast
import tkinter as tk
from tkinter import filedialog
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
        self.tracing_active = True  # Start tracing immediately

    def trace_calls(self, frame, event, arg):
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name

        if func_name not in self.defined_functions:
            return self.trace_calls

        if self.last_func != func_name:
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


def execute_and_trace(file_content, variable_name, defined_functions):
    tracer = RuntimeFlowTracer(variable_name, defined_functions)
    exec_globals = {}
    exec_globals['__name__'] = '__main__'
    sys.settrace(tracer.trace_calls)
    exec(file_content, exec_globals)
    sys.settrace(None)
    return tracer.flow

def visualize_flow(flow, variable_name, current_node=None):
    print(flow)
    G = nx.DiGraph()

    # Count occurrences of the variable
    variable_count = sum(value == variable_name for _, _, value in flow)

    # Create nodes and edges for the graph
    prev_node_label = None
    for func, line_group, value in flow:
        line_range = f"{line_group[0]}-{line_group[-1]}" if len(line_group) > 1 else str(line_group[0])
        node_label = f"{func} (Lines {line_range})"
        G.add_node(node_label)
        if prev_node_label:
            G.add_edge(prev_node_label, node_label)
        prev_node_label = node_label

    pos = nx.spring_layout(G)  # You can try different layouts like circular_layout, random_layout, etc.
    plt.figure(figsize=(12, 8))  # Adjust figure size

    # Determine the color for each node
    node_colors = []
    found_current = False
    for node in G.nodes:
        if node == current_node:
            node_colors.append('green')
            found_current = True
        elif not found_current:
            node_colors.append('red')
        else:
            node_colors.append('blue')

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color='black', arrowstyle='->', arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    # Custom title with variable name and count
    plt.title(f'Tracing "{variable_name}"')
    plt.axis('off')  # Turn off axis
    plt.show()



def main():
    root = tk.Tk()
    root.title("Variable Flow Tracer")
    
    text_widget = tk.Text(root, wrap='none')
    text_widget.pack(expand=True, fill='both')

    def on_file_select():
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                file_content = file.read()
                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', file_content)
                defined_functions = get_defined_functions(file_path)

                def on_text_click(event):
                    try:
                        clicked_index = text_widget.index(tk.CURRENT)
                        line, char = map(int, clicked_index.split('.'))
                        word = text_widget.get(f"{line}.{char-1} wordstart", f"{line}.{char-1} wordend")
                        
                        flow = execute_and_trace(file_content, word, defined_functions)
                        closest_func = find_closest_function(flow, line)
                        visualize_flow(flow, variable_name=word, current_node=closest_func)
                    except Exception as e:
                        print(f"Error: {e}")

                text_widget.bind("<Button-1>", on_text_click)

    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=on_file_select)
    menu_bar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu_bar)

    root.mainloop()

def find_closest_function(flow, line_number):
    closest_func = None
    min_distance = float('inf')
    for func, line_group, _ in flow:
        for line in line_group:
            distance = abs(line - line_number)
            if distance < min_distance:
                min_distance = distance
                line_range = f"{line_group[0]}-{line_group[-1]}" if len(line_group) > 1 else str(line_group[0])
                closest_func = f"{func} (Lines {line_range})"
    return closest_func


if __name__ == "__main__":
    main()
