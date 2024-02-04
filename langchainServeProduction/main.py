from AI import get_outputs
from lcserve import serving

@serving
def ask(text: str, DB_URI: str, **kwargs) -> str:
  return str(get_outputs(text, DB_URI))