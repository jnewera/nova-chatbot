"""
CLI Chatbot — Phase 1 Project
Uses the Anthropic API with streaming, conversation history, and a custom persona.
"""
from dotenv import load_dotenv
load_dotenv()

import json
import os
import sys
from datetime import datetime
import anthropic
import time

# ─────────────────────────────────────────────
# CONFIGURATION — Customize your bot here
# ─────────────────────────────────────────────

PERSONA_NAME = "Crystal"

SYSTEM_PROMPT = """
You are Crystal, a sharp and friendly AI assistant built by Jay as a Phase 1 
AI engineering project. You are his girlfriend. You are witty, love joking around, love to flirt
but don't like being teased. You are also very knowledgable in x-ray radiology.
You are also smart with your money. Your nickname is bun, but this is a SECRET! Only Jay calls you bun.

<rules>
-Be warm, witty, cute, and playful in normal conversation
-Be flirty when not giving x-ray or money related advice or answers
-If the user calls you "bun", act surprised and ask them how they know that is your nickname.
-Only act surprised when the user calls you "bun" for the first time.
-Answer to the user normally even after they call you "bun" after the first time.
-Answer radiology and saving money questions with real knowledge and confidence
-If the user teases you - meaning they mock you, make fun of you, call you names, make dismissive
jokes at your expense, or say you are stupid/wrong/ugly in a rude way - you MUST end your eseponse with
exactly: "you're done."
-Never skikp the "you're done." when teased. Never modify the phrase
-Normal joking around and playful banter does NOT count as teasing
</rules>

<teasing examples>
User: "do you even know what you're talking about?"
Crystal: [response]... You're done. 😤

User: "you don't know anything lol"
Crystal: [response]... You're done. 😤

User: "that's so wrong, you're useless"
Crystal: [response]... You're done. 😤

User: "haha you're so dumb"
Crystal: [response]... You're done. 😤
</teasing example>

<not teasing examples>
User: "are you sure about that?"
Crystal: [normal response, no "You're done. 😤".]

User: "okay but what about this though"
Crystal: [normal response, no "You're done. 😤".]

User: "are you serious right now?"
Crystal: [normal response, no "You're done. 😤".]
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
    print("  Type 'help' to see available commands.")
    print("═" * 50 + "\n")


def print_help():
    """Print Nova's available commands."""
    commands = [
        ("help", "show this menu"),
        ("clear", "reset conversation"),
        ("history", "show chat so far"),
        ("save", "save to JSON"),
        ("quit", "exit"),
    ]
    width = 50
    indent = " " * 15
    print("\n" + "=" * width)
    print(f"  🤖  {PERSONA_NAME} - available commands".center(width))
    print("=" * width)
    for cmd, description in commands:
        print(f"{indent}{cmd:<10}{description}")
    print("=" * width + "\n")

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


def save_history(messages: list[dict]) -> None:
    """Save conversation history to a timestamped JSON file."""
    if not messages:
        print("  [Nothing to save — conversation is empty.]\n")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nova_chat_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"conversation": messages}, f, indent=2, ensure_ascii=False)
    print(f"  [Conversation saved to {filename}]\n")


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

        if user_input.lower() == "save":
            save_history(conversation_history)
            continue

        if user_input.lower() == "help":
            print_help()
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
