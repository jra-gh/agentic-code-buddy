import os

from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite file at file path with content",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to write file content to, relative to the working directory (default is the working directory itself)",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
    ),
)


def write_file(working_directory, file_path, content):
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
            f'    Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        )
    else:
        if os.path.isdir(target_file):
            return_list.append(
                f'    Error: Cannot write to "{file_path}" as it is a directory'
            )
        else:
            target_path = "/".join(target_file.split("/")[:-1])
            os.makedirs(target_path, exist_ok=True)

            f = open(target_file, mode="w")
            f.write(content)
            return_list.append(
                f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
            )

    return "\n".join(return_list)
