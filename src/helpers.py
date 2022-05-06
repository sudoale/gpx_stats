from typing import List
from pathlib import Path
import glob


def get_files_of_format(directory: Path, extension: str) -> List[str]:
    return [Path(file).stem.lower() for file in glob.glob(f'{str(directory)}/*.{extension}')]
