# Telegram Voice Summarizer Bot

A Telegram bot that automatically transcribes and summarizes voice messages longer than 10 seconds using local AI models.

## Features

- 🎤 Transcribes voice messages using OpenAI Whisper large-v3 (optimized for Portuguese)
- 📝 Summarizes transcriptions using Ollama with llama3.1:8b (strict factual mode)
- ⚡ Processes voice messages > 10 seconds automatically
- 🔒 All processing done locally (no external APIs)
- 🇧🇷 Excellent Portuguese language support

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
   ollama pull llama3.1:8b
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
- `whisper.load_model("large-v3")` - Current: best quality for Portuguese. Can change to `medium`, `small`, or `base` for faster processing
- `llama3.1:8b` - Current model. Can use `llama3.2:3b` (faster) or `llama3.2:1b` (even faster but less reliable)
- `voice.duration <= 10` - Change minimum duration threshold

## Models

**Current configuration (optimized for Portuguese accuracy):**
- **Whisper large-v3**: ~3GB, best quality especially for Portuguese
- **llama3.1:8b**: ~4.7GB, excellent accuracy with strict factual prompting

**Alternative models (faster but less accurate):**
- Whisper: `medium` (~1.5GB), `small` (~500MB), `base` (~140MB)
- Ollama: `llama3.2:3b` (~2GB), `llama3.2:1b` (~1.3GB)

**For even better quality:**
- Ollama: `llama3.1:70b` (~40GB) if you have powerful hardware

## License

MIT
