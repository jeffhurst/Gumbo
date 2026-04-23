from dataclasses import dataclass

@dataclass(frozen=True)
class ExpertPromptTemplate:
    system_prompt: str
    task: str
    context: str
    output_format: str

