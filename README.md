# Nova — CLI Chatbot
### Phase 1 AI Engineering Project

A command-line chatbot powered by the Anthropic API.  
Features streaming output, multi-turn conversation memory, and a custom persona.

---

## What this project teaches

| Concept | Where it shows up |
|---|---|
| Environment variables | `os.environ.get("ANTHROPIC_API_KEY")` |
| Dicts and lists | `conversation_history: list[dict]` |
| Functions with return values | `stream_response()` returns the full text |
| Error handling | `try/except` around the API call |
| While loops | The main chat loop |
| f-strings | Used throughout for output |
| Importing modules | `import anthropic`, `import os` |

---

## Setup (do this once)

**1. Clone the repo and navigate into it**
```bash
git clone https://github.com/YOUR_USERNAME/nova-chatbot.git
cd nova-chatbot
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set your API key**  
Get yours at https://console.anthropic.com

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # Mac/Linux (add to ~/.zshrc to persist)
set ANTHROPIC_API_KEY=sk-ant-...        # Windows CMD
```

---

## Run it

```bash
python chatbot.py
```

You'll see the Nova banner and a `You:` prompt.

### Commands

| Type this | What happens |
|---|---|
| Anything | Chat with Nova |
| `clear` | Reset conversation history |
| `history` | See all messages so far |
| `quit` / `exit` | Exit the chatbot |
| `Ctrl+C` | Exit immediately |

---

## How it works

```
You type a message
       ↓
Your message is added to conversation_history (a list of dicts)
       ↓
The ENTIRE history is sent to the Anthropic API on every call
(this is how the model "remembers" — it re-reads everything each time)
       ↓
The API streams back a response chunk by chunk
       ↓
Each chunk is printed immediately (streaming effect)
       ↓
The full response is added to conversation_history
       ↓
Loop back to the top
```

---

## Customize your bot

Open `chatbot.py` and change:

- **`PERSONA_NAME`** — your bot's name
- **`SYSTEM_PROMPT`** — its personality, rules, and knowledge
- **`MODEL`** — try `claude-haiku-4-5-20251001` for faster/cheaper responses
- **`MAX_TOKENS`** — controls max response length

---

## Git workflow used in this project

```bash
git init
git add .
git commit -m "feat: initial CLI chatbot with streaming"

# Push to GitHub (after creating the repo on github.com)
git remote add origin https://github.com/YOUR_USERNAME/nova-chatbot.git
git push -u origin main
```

**Good commit message format:**
```
feat: add clear and history commands
fix: handle rate limit error gracefully
refactor: extract stream_response into its own function
docs: update README with setup steps
```

---

## Next steps (Phase 2 hooks)

- [ ] Add a `--persona` flag via `argparse` so you can switch personas at launch
- [ ] Save conversation history to a `.json` file so it persists between sessions
- [ ] Wrap the API call in a FastAPI endpoint so other apps can talk to your bot
- [ ] Add tool use so the bot can search the web or read files
