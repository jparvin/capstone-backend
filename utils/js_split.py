from pydantic import BaseModel
import re


class FunctionBody(BaseModel):
    name: str
    params: list[str]
    start_line: int
    end_line: int | None
    file_name: str
    return_type: str | None = None

    def to_dict(self):
        return {
            'name': self.name,
            'params': self.params,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'file_name': self.file_name,
            'return_type': self.return_type
        }

def load_file(file_name: str):
    functions: list[FunctionBody] = []
    with open(file_name, 'r') as file:
        content = file.readlines()

    function_expression_pattern = r'\b(\w+)\s*:\s*function\s*\(([^)]*)\)\s*{'
    function_declaration_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*{'
    comment_pattern = r'^\s*//'
    active_functions = []
    brace_counts = []

    for current_line, line in enumerate(content, start=1):
        if not re.match(comment_pattern, line):
            if active_functions:
                brace_counts[-1] += line.count('{')
                brace_counts[-1] -= line.count('}')

                if brace_counts[-1] == 0:
                    active_functions[-1].end_line = current_line
                    functions.append(active_functions.pop())
                    brace_counts.pop()
            if not active_functions or brace_counts[-1] == 0:
                exp_match = re.search(function_expression_pattern, line)
                funct_match = re.search(function_declaration_pattern, line)
                if exp_match:
                    function_name = exp_match.group(1)
                    parameters = exp_match.group(2).split(',') if exp_match.group(2) else []
                    active_function = FunctionBody(
                        name=function_name,
                        params=[param.strip() for param in parameters],
                        start_line=current_line,
                        end_line=None,
                        file_name=file_name
                    )
                    active_functions.append(active_function)
                    brace_counts.append(1)  # account for the opening brace
                elif funct_match:
                    function_name = funct_match.group(1)
                    parameters = funct_match.group(2).split(',') if funct_match.group(2) else []
                    active_function = FunctionBody(
                        name=function_name,
                        params=[param.strip() for param in parameters],
                        start_line=current_line,
                        end_line=None,
                        file_name=file_name
                    )
                    active_functions.append(active_function)
                    brace_counts.append(1)  # account for the opening brace

    return functions

functions = (load_file('sample_code/sample.js'))

for function in functions:
    print(function.to_dict())