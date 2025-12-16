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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configure Ollama client
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)
logger.info(f"Using Ollama host: {ollama_host}")

# Load Whisper model (using large-v3 for better Portuguese accuracy)
logger.info("Loading Whisper model...")
whisper_model = whisper.load_model("large-v3")
logger.info("Whisper model loaded")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    try:
        voice = update.message.voice
        chat = update.message.chat
        user = update.message.from_user

        # Log for debugging
        logger.info(
            f"Voice message in {chat.type} chat (ID: {chat.id}, Title: {chat.title}), "
            f"from {user.username or user.first_name}, duration: {voice.duration}s"
        )

        # Check if voice message is longer than 10 seconds
        if voice.duration <= 10:
            logger.info(f"Voice message too short ({voice.duration}s), ignoring")
            return

        logger.info(f"Processing voice message ({voice.duration}s)")
        
        # React to message while processing
        await update.message.set_reaction("🙉")
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
            result = whisper_model.transcribe(
                str(wav_path),
                language="pt",
                task="transcribe",
                temperature=0.0,  # More deterministic
                condition_on_previous_text=True,  # Better context
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6,
            )
            transcription = result["text"].strip()

            if not transcription:
                logger.info("Empty transcription, ignoring")
                return

            logger.info(f"Transcription: {transcription}")

            # Extract core idea with local LLM
            logger.info("Extracting core idea...")
            prompt = f"""Você é um assistente que extrai a ideia central de transcrições de áudio.

REGRAS IMPORTANTES:
1. Extraia APENAS a informação ou ideia mais importante e relevante
2. IGNORE: reclamações vagas, divagações, enchimento de linguiça, conversas casuais sem conteúdo
3. Se houver uma pergunta, decisão, pedido, anúncio ou informação concreta: extraia isso
4. Se for apenas conversa vaga sem conteúdo relevante: responda "Sem conteúdo relevante"
5. Baseie-se APENAS no que foi dito, não invente nada
6. Use no máximo 1-2 frases diretas
7. Seja objetivo e factual

Transcrição:
{transcription}

Ideia central (ou "Sem conteúdo relevante"):"""

            response = ollama_client.generate(
                model="llama3.1:8b",  # Larger model for better accuracy and comprehension
                prompt=prompt,
                options={
                    "temperature": 0.0,  # No creativity - purely deterministic
                    "top_p": 0.1,  # Very focused sampling
                    "top_k": 10,  # Consider only top 10 tokens
                    "repeat_penalty": 1.1,  # Slight penalty for repetition
                },
            )
            core_idea = response["response"].strip()

            # Format and send response
            await status_msg.edit_text(f"💡 {core_idea}")
            logger.info(f"Core idea sent: {core_idea}")

    except Exception as e:
        logger.error(f"Error processing voice message: {e}", exc_info=True)


def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    # Create application
    application = Application.builder().token(token).build()

    # Add voice message handler
    application.add_handler(
        MessageHandler(filters.VOICE & (~filters.COMMAND), handle_voice)
    )

    logger.info("Bot started, listening for voice messages...")
    logger.info("Make sure Group Privacy is DISABLED in @BotFather with /setprivacy")
    application.run_polling()


if __name__ == "__main__":
    main()
