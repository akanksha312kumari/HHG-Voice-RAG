"""Tool abstraction for the pipeline."""
from typing import Any, Dict, Optional
from pydantic import BaseModel

class PipelineTool(BaseModel):
    """Pipeline tool abstraction."""
    name: str
    timeout_ms: int
    retry_config: Optional[Dict[str, Any]] = None
    input_schema: Optional[Any] = None
    output_schema: Optional[Any] = None
    
    # TODO: Implement tool execution patterns
