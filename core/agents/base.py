"""
AegisCortex AI - Base Agent Definition
Standard interface, data models, and telemetry for multi-agent swarm workers.
"""

from abc import ABC, abstractmethod
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    doc_title: str
    section_name: str
    file_name: Optional[str] = None
    verbatim_text: str
    relevance_score: float = 1.0

class AgentResult(BaseModel):
    agent_name: str
    status: str = "SUCCESS"  # SUCCESS, WARNING, CRITICAL_ALERT, NO_DATA
    summary: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    citations: List[Citation] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    confidence_score: float = 1.0

class BaseAgent(ABC):
    def __init__(self, client):
        self.client = client
        self.name = self.__class__.__name__

    def run(self, context: Dict[str, Any]) -> AgentResult:
        start_time = time.time()
        try:
            result = self.execute(context)
            result.execution_time_ms = round((time.time() - start_time) * 1000, 2)
            return result
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return AgentResult(
                agent_name=self.name,
                status="ERROR",
                summary=f"Execution error in {self.name}: {str(e)}",
                structured_data={"error": str(e)},
                execution_time_ms=elapsed,
                confidence_score=0.0
            )

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Core execution logic implemented by specialized agent."""
        pass
