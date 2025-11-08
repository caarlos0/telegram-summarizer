# Telegram Voice Summarizer Bot

A Telegram bot that automatically transcribes and summarizes voice messages longer than 10 seconds using local AI models.

## Features

- 🎤 Transcribes voice messages using OpenAI Whisper (local)
- 📝 Summarizes transcriptions using Ollama with llama3.2:1b
- ⚡ Processes voice messages > 10 seconds automatically
- 🔒 All processing done locally (no external APIs)

## Prerequisites

1. **Python 3.10+**
2. **uv** - Fast Python package installer
3. **Ollama** - For running local LLM
   ```bash
   # Install Ollama (macOS)
   brew install ollama
   
   # Start Ollama service
   ollama serve
   
   # Pull the model (in another terminal)
   ollama pull llama3.2:1b
   ```

4. **FFmpeg** - For audio conversion
   ```bash
   # macOS
   brew install ffmpeg
   ```

## Setup

1. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

2. **Create a Telegram bot:**
   - Talk to [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the bot token

3. **Set environment variable:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your-token-here"
   # Optional: Set custom Ollama host (defaults to http://localhost:11434)
   export OLLAMA_HOST="http://localhost:11434"
   ```

4. **Add bot to group:**
   - Add your bot to a Telegram group
   - Make sure the bot has permission to read messages

## Usage

Run the bot:
```bash
telegram-summarizer
# or
python -m telegram_summarizer
```

The bot will:
1. Listen for voice messages in groups
2. Ignore messages <= 10 seconds
3. For longer messages:
   - Download and transcribe the audio
   - Generate a concise summary
   - Reply with both summary and full transcription

## Configuration

**Environment variables:**
- `TELEGRAM_BOT_TOKEN` - Your bot token (required)
- `OLLAMA_HOST` - Ollama server URL (optional, defaults to `http://localhost:11434`)

**Code customization** - Edit `src/telegram_summarizer/__main__.py`:
- `whisper.load_model("base")` - Change to `tiny`, `small`, `medium`, or `large`
- `llama3.2:1b` - Use different Ollama models (e.g., `llama3.2:3b` for better quality)
- `voice.duration <= 10` - Change minimum duration threshold

## Models

- **Whisper base**: ~140MB, good balance of speed/accuracy
- **llama3.2:1b**: ~1.3GB, fast inference for summaries

For better quality, use larger models (at cost of speed):
- Whisper: `small` or `medium`
- Ollama: `llama3.2:3b` or `llama3.1:8b`

## License

MIT
