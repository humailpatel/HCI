import ast

def oparse_python_file(file_path):
    with open(file_path, "r") as source:
        code = source.read()
        tree = ast.parse(code)
    
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    variables = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    if var_name not in variables:
                        variables[var_name] = []
                    variables[var_name].append((file_path, target.lineno))

    return functions, variables, code.split('\n')