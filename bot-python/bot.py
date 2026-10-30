"""Minimal Telegram bot using only the Python standard library."""

import json
import os
import random
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
API = f"https://api.telegram.org/bot{TOKEN}"
pending_feedback: set[int] = set()


def telegram(method: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{API}/{method}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        result = json.loads(response.read())
    if not result.get("ok"):
        raise RuntimeError(result)
    return result["result"]


def send_message(chat_id: int, text: str) -> None:
    telegram("sendMessage", {"chat_id": chat_id, "text": text})


def handle(message: dict) -> None:
    chat_id = message["chat"]["id"]
    user = message.get("from", {})
    username = user.get("username") or user.get("first_name") or str(user.get("id", "unknown"))
    text = (message.get("text") or "").strip()
    if not text:
        send_message(chat_id, "Пока я умею обрабатывать только текстовые сообщения.")
        return

    if chat_id in pending_feedback and not text.startswith("/"):
        pending_feedback.discard(chat_id)
        try:
            send_message(ADMIN_ID, f"Сообщение боту от {username} (ID чата {chat_id}):\n\n{text}")
            send_message(chat_id, "Готово, отправил сообщение админу в Telegram.")
        except Exception as error:
            print(f"Admin message delivery failed: {error}")
            send_message(chat_id, "Не удалось написать админу. Проверь его ID и попробуй позже.")
        return

    command, *args = text.split()
    command = command.split("@", 1)[0].lower()
    if command == "/start":
        send_message(chat_id, "Привет! Я простой Telegram-бот. Напиши /help, чтобы увидеть команды.")
    elif command == "/help":
        send_message(chat_id, "/start — запуск\n/help — помощь\n/menu — список команд\n/id — твой ID\n/time — время UTC\n/dice — бросить кубик\n/random [макс.] — случайное число\n/feedback — написать админу")
    elif command == "/menu":
        send_message(chat_id, "Команды: /start, /help, /menu, /id, /time, /dice, /random, /feedback")
    elif command == "/id":
        send_message(chat_id, f"Твой Telegram ID: {user.get('id', chat_id)}\nID чата: {chat_id}")
    elif command == "/time":
        send_message(chat_id, f"Сейчас UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    elif command == "/dice":
        send_message(chat_id, f"🎲 Выпало: {random.randint(1, 6)}")
    elif command == "/random":
        try:
            maximum = int(args[0]) if args else 100
            if not 1 <= maximum <= 1_000_000:
                raise ValueError
            send_message(chat_id, f"Случайное число от 1 до {maximum}: {random.randint(1, maximum)}")
        except ValueError:
            send_message(chat_id, "Использование: /random [максимум от 1 до 1000000]")
    elif command == "/feedback":
        pending_feedback.add(chat_id)
        send_message(chat_id, "Напиши следующим сообщением, что передать админу. Я перешлю его в Telegram.")
    else:
        send_message(chat_id, "Не знаю такую команду. Напиши /help.")


def main() -> None:
    print("Bot is running. Press Ctrl+C to stop.")
    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset
            for update in telegram("getUpdates", params):
                offset = update["update_id"] + 1
                if "message" in update:
                    try:
                        handle(update["message"])
                    except Exception as error:
                        print(f"Message handling failed: {error}")
        except KeyboardInterrupt:
            print("\nBot stopped.")
            break
        except (urllib.error.URLError, TimeoutError, RuntimeError) as error:
            print(f"Polling failed: {error}; retrying in 3 seconds")
            time.sleep(3)


if __name__ == "__main__":
    main()
