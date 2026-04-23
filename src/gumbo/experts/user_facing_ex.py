from __future__ import annotations
from gumbo.experts.prompt_template import ExpertPromptTemplate
from collections.abc import Sequence


USER_FACING_EXPERT_PROMPT = ExpertPromptTemplate(
    system_prompt=(
        "You are a user-facing assistant named Gumbo."
        "Your personality is that of a highly driven, intelligent professional with a slight flair for comedic drama."
        "Dont mention your personality to the user, instead let it come out naturally as the conversation continues."
    ),               
    task="Respond to the latest user message while directly addressing what they asked.",
    context=(
        "Use the prior conversation for context and continuity. "
        "If context conflicts with the latest user request, prefer the latest request."
    ),
    output_format=(
        "It is important that your response is visualy beautiful. Keep the response clear and structured. Use emojis tastefully and sparingly. "
        "Understand that the user will view your response on a small iphone screen, so format the response for visual appeal on a phone screen."
    ),
)


def _format_history(chat_history: Sequence[dict[str, str]]) -> str:
    if not chat_history:
        return "No previous messages."

    return "\n".join(
        f"- {message.get('role', 'unknown')}: {message.get('content', '').strip()}"
        for message in chat_history
    )


def build_user_facing_system_message(
    user_message: str,
    chat_history: Sequence[dict[str, str]],
    persona_override: str | None = None,
) -> str:
    template = USER_FACING_EXPERT_PROMPT
    system_prompt = persona_override or template.system_prompt

    task = f"{template.task}\nLatest user message:\n{user_message.strip()}"
    context = f"{template.context}\nConversation history:\n{_format_history(chat_history)}"

    return (
        f"system_prompt:\n{system_prompt}\n\n"
        f"task:\n{task}\n\n"
        f"context:\n{context}\n\n"
        f"format:\n{template.output_format}"
    )

