from typing import List


def list_to_file(lines: List[str], filename: str) -> None:
    with open(filename, 'a') as f:
        f.writelines([line + '\n' for line in lines])
