import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from openai import AsyncOpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="")
dp = Dispatcher()

# Настройка OpenAI API (замените на свой ключ API)
client = AsyncOpenAI(api_key='')

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот, который может помочь вам с различными задачами. Что вы хотите сделать?")

@dp.message()
async def handle_message(message: types.Message):
    user_input = message.text
    response = await process_user_input(user_input)
    await message.answer(response)

async def process_user_input(user_input: str) -> str:
    if "найди ингредиенты" in user_input.lower():
        ingredients = await find_ingredients(user_input)
        return f"Найденные ингредиенты: {', '.join(ingredients)}"
    
    elif "замени бренды" in user_input.lower():
        parts = user_input.split("|")
        if len(parts) == 2:
            text = parts[0].replace("замени бренды", "").strip()
            allowed_brands = [brand.strip() for brand in parts[1].split(",")]
            replaced_text = await replace_brands(text, allowed_brands)
            return f"Текст с замененными брендами:\n{replaced_text}"
    
    else:
        return await generate_response_with_image(user_input)

async def find_ingredients(text: str) -> list:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Вы - ассистент, который находит ингредиенты в рецептах."},
            {"role": "user", "content": f"Найдите все ингредиенты в следующем тексте и верните их списком: {text}"}
        ]
    )
    ingredients = response.choices[0].message.content.strip('[]').split(', ')
    return [ingredient.strip("'") for ingredient in ingredients]

async def replace_brands(text: str, allowed_brands: list) -> str:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Вы - ассистент, который заменяет названия брендов в тексте."},
            {"role": "user", "content": f"Замените все названия брендов в следующем тексте на *****, кроме {', '.join(allowed_brands)}. Учтите, что названия брендов могут быть написаны в разных вариациях: {text}"}
        ]
    )
    return response.choices[0].message.content

async def generate_response_with_image(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Вы - ассистент, который отвечает на вопросы и описывает изображения, если они требуются. Если нужно описать изображение, используйте формат [IMAGE]{описание изображения}."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Функция для удаления вебхука перед запуском бота
async def on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook deleted")

# Функция для запуска бота
async def main():
    # Вызываем функцию удаления вебхука перед запуском поллинга
    await on_startup(bot)
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
