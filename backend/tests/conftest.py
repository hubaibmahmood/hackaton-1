import sys
import os
from pathlib import Path

# Add backend root to sys.path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))
