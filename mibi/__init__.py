from pathlib import Path
from importlib_metadata import version

__version__ = version("mibi-bioasq")

PROJECT_DIR = Path(__file__).parent.parent
