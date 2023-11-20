import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt

def display_file_contents(file_contents, all_variables, current_file):
    root = tk.Tk()
    root.title(f"File Contents: {current_file}")

    text = tk.Text(root, wrap="none")
    text.pack(expand=True, fill="both")

    def on_click(event, word):
        return show_related_files(word, all_variables, current_file)

    for i, line in enumerate(file_contents, 1):
        text.insert(f"{i}.0", f"{line}\n")
        for word in line.split():
            if word in all_variables:
                start_index = f"{i}.{line.find(word)}"
                end_index = f"{i}.{line.find(word) + len(word)}"
                text.tag_add(word, start_index, end_index)
                text.tag_bind(word, "<Button-1>", lambda event, word=word: on_click(event, word))

    text.config(state="disabled")  # Make the text widget read-only
    root.mainloop()

def show_related_files(variable, all_variables, current_file):
    related_files = all_variables[variable]
    file_list = "\n".join([f"{path} (line {line})" for path, line in related_files])
    tk.messagebox.showinfo(title=f"Occurrences of '{variable}'", message=file_list)

    create_and_show_graph(all_variables, current_file)

def create_and_show_graph(all_variables, current_file):
    G = nx.DiGraph()

    # Add nodes for each file and edges for shared variables
    for variable, occurrences in all_variables.items():
        for (file_path, line) in occurrences:
            if file_path == current_file:
                for (other_file_path, _) in occurrences:
                    if other_file_path != current_file:
                        G.add_edge(current_file, other_file_path, label=variable)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.show()