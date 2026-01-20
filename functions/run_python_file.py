import os
import subprocess

from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute Python file at given file path with optional arguments",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to Python file to execute, relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional array of arguments to pass to the Python file at execution",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
    except Exception:
        return f'Error: "{working_directory}" is not a directory'

    try:
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
    except Exception:
        return f'Error: File not found or is not a regular file: "{file_path}"'

    valid_target_dir = (
        os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    )
    return_list = [f'Result for "{file_path}" file:']
    if not valid_target_dir:
        return_list.append(
            f'    Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        )
    else:
        if not os.path.isfile(target_file):
            return_list.append(
                f'    Error: "{file_path}" does not exist or is not a regular file'
            )
        elif not target_file.endswith(".py"):
            return_list.append(f'    Error: "{file_path}" is not a Python file')
        else:
            command = ["python", target_file]
            if args:
                command.extend(args)

            try:
                complete = subprocess.run(
                    command, capture_output=True, text=True, timeout=30
                )
                if complete.returncode != 0:
                    return_list.append(
                        f"    Process exited with code {complete.returncode}"
                    )
                elif complete.stdout == "" and complete.stderr == "":
                    return_list.append("    No output produced")
                else:
                    if complete.stdout != "":
                        return_list.append(f"STDOUT:\n{complete.stdout}")
                    if complete.stderr != "":
                        return_list.append(f"STDERR:\n{complete.stderr}")
            except Exception as e:
                return_list.append(f"    Error: executing Python file: {e}")

    return "\n".join(return_list)
