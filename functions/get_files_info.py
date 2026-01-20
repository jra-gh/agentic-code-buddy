import os

from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):
    try:
        working_dir_abs = os.path.abspath(working_directory)
    except Exception:
        return f'Error: "{working_directory}" is not a directory'

    try:
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
    except Exception:
        return f'Error: "{directory}" is not a directory'

    valid_target_dir = (
        os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
    )

    return_list = [
        f"Result for {'current' if directory == '.' else f"'{directory}'"} directory:"
    ]

    if not valid_target_dir:
        return_list.append(
            f'    Error: Cannot list "{directory}" as it is outside the permitted working directory'
        )
    else:
        for item in os.listdir(target_dir):
            target_item = os.path.join(target_dir, item)
            return_list.append(
                f"  - {item}: file_size={os.path.getsize(target_item)} bytes, is_dir={os.path.isdir(target_item)}"
            )

    return "\n".join(return_list)
