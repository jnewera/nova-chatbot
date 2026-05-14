"""
CLI Chatbot — Phase 1 Project
Uses the Anthropic API with streaming, conversation history, and a custom persona.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import anthropic

# ─────────────────────────────────────────────
# CONFIGURATION — Customize your bot here
# ─────────────────────────────────────────────

PERSONA_NAME = "Nova"

SYSTEM_PROMPT = """
You are Nova, a sharp and friendly AI assistant built by Jay as a Phase 1 
AI engineering project. You are concise, technically sharp, and occasionally 
witty. When asked about code, you explain it clearly. You never pretend to 
know things you don't.
""".strip()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def print_banner():
    """Print the welcome banner when the chatbot starts."""
    print("\n" + "═" * 50)
    print(f"  🤖  {PERSONA_NAME} — CLI Chatbot")
    print("  Type 'quit' or 'exit' to leave.")
    print("  Type 'clear' to reset conversation history.")
    print("  Type 'history' to see the conversation so far.")
    print("═" * 50 + "\n")


def print_history(messages: list[dict]) -> None:
    """Print the full conversation history."""
    if not messages:
        print("  [No conversation history yet.]\n")
        return
    print("\n" + "─" * 40)
    for msg in messages:
        role = "You" if msg["role"] == "user" else PERSONA_NAME
        print(f"  [{role}] {msg['content']}")
    print("─" * 40 + "\n")


def stream_response(client: anthropic.Anthropic, messages: list[dict]) -> str:
    """
    Call the Anthropic API with streaming enabled.
    Prints each chunk as it arrives, then returns the full response.

    Streaming means you see output word-by-word (like Claude.ai does),
    rather than waiting for the entire response to finish.
    """
    full_response = ""

    print(f"\n{PERSONA_NAME}: ", end="", flush=True)

    # context manager streams the response chunk by chunk
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text_chunk in stream.text_stream:
            print(text_chunk, end="", flush=True)
            full_response += text_chunk

    print("\n")  # newline after the streamed response ends
    return full_response


# ─────────────────────────────────────────────
# MAIN CHAT LOOP
# ─────────────────────────────────────────────

def main():
    # 1. Get the API key from an environment variable
    #    Never paste your actual key into code — that's a security risk.
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌  Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("    Run: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # 2. Create the Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # 3. conversation_history holds all turns of the chat.
    #    Each entry is a dict: {"role": "user" | "assistant", "content": "..."}
    #    The full history is sent on every API call — that's how the model
    #    "remembers" what was said earlier.
    conversation_history: list[dict] = []

    print_banner()

    # 4. The main loop — keeps running until the user types 'quit'
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C or Ctrl+D exits cleanly
            print(f"\n\n{PERSONA_NAME}: See you later! 👋\n")
            break

        # Handle empty input — just loop again
        if not user_input:
            continue

        # Handle special commands
        if user_input.lower() in ("quit", "exit"):
            print(f"\n{PERSONA_NAME}: See you later! 👋\n")
            break

        if user_input.lower() == "clear":
            conversation_history.clear()
            print(f"\n  [Conversation cleared. Fresh start!]\n")
            continue

        if user_input.lower() == "history":
            print_history(conversation_history)
            continue

        # 5. Add the user's message to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # 6. Call the API and stream the response
        try:
            response_text = stream_response(client, conversation_history)
        except anthropic.APIConnectionError:
            print("❌  Connection error. Check your internet and try again.\n")
            conversation_history.pop()  # remove the failed message
            continue
        except anthropic.AuthenticationError:
            print("❌  Bad API key. Double-check your ANTHROPIC_API_KEY.\n")
            sys.exit(1)
        except anthropic.RateLimitError:
            print("❌  Rate limit hit. Wait a moment and try again.\n")
            conversation_history.pop()
            continue

        # 7. Add the assistant's response to history for next turn
        conversation_history.append({
            "role": "assistant",
            "content": response_text
        })


if __name__ == "__main__":
    main()
