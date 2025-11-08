#!/usr/bin/env python3
import os
import logging
from pathlib import Path
import tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import whisper
import ollama
from pydub import AudioSegment

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Whisper model (using base model for balance of speed/accuracy)
logger.info("Loading Whisper model...")
whisper_model = whisper.load_model("base")
logger.info("Whisper model loaded")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    try:
        voice = update.message.voice
        chat = update.message.chat
        user = update.message.from_user
        
        # Log for debugging
        logger.info(f"Voice message in {chat.type} chat (ID: {chat.id}, Title: {chat.title}), "
                   f"from {user.username or user.first_name}, duration: {voice.duration}s")

        # Check if voice message is longer than 10 seconds
        if voice.duration <= 10:
            logger.info(f"Voice message too short ({voice.duration}s), ignoring")
            return

        logger.info(f"Processing voice message ({voice.duration}s)")

        # Send a "processing" message
        status_msg = await update.message.reply_text("🎤 Transcrevendo e resumindo...")
    except Exception as e:
        logger.error(f"Error in initial setup: {e}", exc_info=True)
        return

    try:
        # Download voice message
        voice_file = await context.bot.get_file(voice.file_id)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Download as .oga file
            oga_path = tmp_path / "voice.oga"
            await voice_file.download_to_drive(oga_path)

            # Convert to wav for Whisper
            wav_path = tmp_path / "voice.wav"
            audio = AudioSegment.from_file(oga_path)
            audio.export(wav_path, format="wav")

            # Transcribe with Whisper
            logger.info("Transcribing audio...")
            result = whisper_model.transcribe(str(wav_path), language="pt")
            transcription = result["text"].strip()

            if not transcription:
                await status_msg.edit_text("⚠️ Não foi possível transcrever o áudio")
                return

            logger.info(f"Transcription: {transcription[:100]}...")

            # Summarize with local LLM
            logger.info("Generating summary...")
            prompt = f"""Resuma a seguinte transcrição de mensagem de voz de forma concisa em 2-3 frases:

{transcription}

Resumo:"""

            response = ollama.generate(
                model='llama3.2:1b',  # Using smaller model for speed
                prompt=prompt
            )
            summary = response['response'].strip()

            # Format and send response
            await status_msg.edit_text(f"📝 {summary}")
            logger.info("Summary sent successfully")

    except Exception as e:
        logger.error(f"Error processing voice message: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Erro ao processar áudio: {str(e)}")


def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    # Create application
    application = Application.builder().token(token).build()

    # Add voice message handler
    application.add_handler(MessageHandler(filters.VOICE & (~filters.COMMAND), handle_voice))

    logger.info("Bot started, listening for voice messages...")
    logger.info("Make sure Group Privacy is DISABLED in @BotFather with /setprivacy")
    application.run_polling()


if __name__ == "__main__":
    main()
