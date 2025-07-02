# tamagotchi_scheduler.py
import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import utils.httpx_proxy_patch
from supabase import create_client, Client
from telegram import Bot
import random
from pathlib import Path
from dotenv import load_dotenv

# Московское время (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))

def get_moscow_time():
    """Получить текущее время в Москве"""
    return datetime.now(MOSCOW_TZ)

if Path('.env').is_file():
    load_dotenv()      # локальная разработка

# Настройки логирования
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not all([TELEGRAM_TOKEN, SUPABASE_URL, SUPABASE_KEY]):
    raise Exception("Не хватает переменных окружения!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

async def get_tamagotchi_message(message_type):
    """Получить случайное сообщение тамагочи"""
    try:
        result = supabase.table("tamagotchi_messages").select("*").eq("message_type", message_type).execute()
        if result.data:
            message_data = random.choice(result.data)
            return f"{message_data['emoji']} {message_data['message']}"
        return "🐾 Тамагочи что-то говорит..."
    except Exception as e:
        logging.exception("Ошибка получения сообщения тамагочи:")
        return "🐾 Тамагочи молчит..."

async def check_hungry_tamagotchis():
    """Проверить голодных тамагочи и отправить уведомления"""
    try:
        logging.info("Проверка голодных тамагочи...")
        
        # Получить всех живых тамагочи
        result = supabase.table("tamagotchi").select("*").eq("is_alive", True).execute()
        
        if not result.data:
            logging.info("Тамагочи не найдены")
            return
        
        now = get_moscow_time().replace(tzinfo=None)
        
        for tamagotchi in result.data:
            try:
                # Рассчитать время с последнего кормления
                last_fed = datetime.fromisoformat(tamagotchi["last_fed"])
                if last_fed.tzinfo is not None:
                    last_fed = last_fed.replace(tzinfo=None)
                
                hours_since_fed = (now - last_fed).total_seconds() / 3600
                
                # Обновить показатели
                hunger = max(0, tamagotchi["hunger"] - int(hours_since_fed * 5))
                happiness = max(0, tamagotchi["happiness"] - int(hours_since_fed * 3))
                health = max(0, tamagotchi["health"] - int(hours_since_fed * 2))
                
                # Проверить смерть (3 дня = 72 часа)
                is_alive = hours_since_fed < 72
                
                # Обновить в базе
                updated_data = {
                    "hunger": hunger,
                    "happiness": happiness,
                    "health": health,
                    "is_alive": is_alive,
                    "updated_at": now.isoformat()
                }
                
                supabase.table("tamagotchi").update(updated_data).eq("telegram_id", tamagotchi["telegram_id"]).execute()
                
                # Получить chat_id пользователя
                user_result = supabase.table("users").select("chat_id").eq("telegram_id", tamagotchi["telegram_id"]).execute()
                if not user_result.data or not user_result.data[0].get("chat_id"):
                    continue
                
                chat_id = user_result.data[0]["chat_id"]
                
                # Отправить уведомления в зависимости от состояния
                if not is_alive:
                    # Тамагочи умер
                    message = await get_tamagotchi_message("dead")
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"💀 **Ваш тамагочи умер!**\n\n{message}\n\nВы не сканировали QR-коды более 3 дней. Воскресите его следующим сканированием!",
                        parse_mode='Markdown'
                    )
                    logging.info(f"Отправлено уведомление о смерти тамагочи пользователю {tamagotchi['telegram_id']}")
                    
                elif hunger < 20 or happiness < 20 or health < 20:
                    # Тамагочи очень голоден/болен
                    message = await get_tamagotchi_message("sick")
                    status_text = f"""
😰 **{tamagotchi['name']}** (Уровень {tamagotchi['level']}) - КРИТИЧЕСКОЕ СОСТОЯНИЕ!
🍎 Сытость: {hunger}/100
😊 Счастье: {happiness}/100
❤️ Здоровье: {health}/100

{message}

⚠️ Срочно отсканируйте QR-код на работе, иначе тамагочи умрет!
                    """.strip()
                    
                    await bot.send_message(
                        chat_id=chat_id,
                        text=status_text,
                        parse_mode='Markdown'
                    )
                    logging.info(f"Отправлено критическое уведомление пользователю {tamagotchi['telegram_id']}")
                    
                elif hunger < 50 or happiness < 50 or health < 50:
                    # Тамагочи голоден
                    message = await get_tamagotchi_message("hungry")
                    status_text = f"""
😔 **{tamagotchi['name']}** (Уровень {tamagotchi['level']}) - голоден
🍎 Сытость: {hunger}/100
😊 Счастье: {happiness}/100
❤️ Здоровье: {health}/100

{message}

Не забывайте сканировать QR-коды на работе!
                    """.strip()
                    
                    # Отправляем уведомления о голоде только раз в 6 часов
                    if hours_since_fed > 6 and int(hours_since_fed) % 6 == 0:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=status_text,
                            parse_mode='Markdown'
                        )
                        logging.info(f"Отправлено уведомление о голоде пользователю {tamagotchi['telegram_id']}")
                
            except Exception as e:
                logging.exception(f"Ошибка обработки тамагочи пользователя {tamagotchi['telegram_id']}:")
                continue
        
        logging.info("Проверка тамагочи завершена")
        
    except Exception as e:
        logging.exception("Ошибка проверки тамагочи:")

async def main():
    """Основной цикл проверки тамагочи"""
    logging.info("Запуск планировщика тамагочи...")
    
    while True:
        try:
            await check_hungry_tamagotchis()
            # Проверяем каждый час
            await asyncio.sleep(3600)  # 1 час = 3600 секунд
        except Exception as e:
            logging.exception("Ошибка в основном цикле:")
            # При ошибке ждем 5 минут и пробуем снова
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
