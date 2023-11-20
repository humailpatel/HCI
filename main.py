from gui import *
from parseText import *

def main():
    file_paths = ["sampleFile.py", "sampleFile2.py"]
    all_functions = set()
    all_variables = {}

    for file_path in file_paths:
        functions, variables, code = parse_python_file(file_path)
        all_functions.update(functions)

        for var, locations in variables.items():
            if var not in all_variables:
                all_variables[var] = locations
            else:
                all_variables[var].extend(locations)

    # For demonstration, let's just display the contents of the first file
    current_file = file_paths[0]
    display_file_contents(code, all_variables, current_file)

if __name__ == "__main__":
    main()