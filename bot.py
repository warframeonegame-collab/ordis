import discord
from discord.ext import commands, tasks
import os
import asyncio
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("Токен не найден в файле .env!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True
intents.voice_states = True
intents.presences = True

bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command("help")

async def load_cogs():
    try:
        cog_files = [f for f in os.listdir('cogs') if f.endswith('.py')]
        
        for cog in cog_files:
            cog_name = f'cogs.{cog[:-3]}'
            try:
                await bot.load_extension(cog_name)
                logging.info(f'✅ Успешно загружен Cog: {cog_name}')
            except commands.ExtensionNotFound:
                logging.error(f'❌ Cog не найден: {cog_name}')
            except commands.ExtensionAlreadyLoaded:
                logging.warning(f'⚠️ Cog уже загружен: {cog_name}')
            except commands.NoEntryPointError:
                logging.error(f'❌ Отсутствует точка входа в Cog: {cog_name}')
            except Exception as e:
                logging.error(f'❌ Ошибка при загрузке Cog {cog_name}: {str(e)}')
                
    except Exception as e:
        logging.critical(f'❌ Критическая ошибка при загрузке Cogs: {str(e)}')

@bot.event
async def on_ready():
    logging.info(f'🤖 Бот {bot.user} успешно авторизован!')
    logging.info(f'ID бота: {bot.user.id}')
    logging.info('--- Загружаю расширения... ---')

    await load_cogs()

    await bot.change_presence(activity=discord.Game(name="Warframe"))
    logging.info('Статус установлен: Играет в Warframe')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для выполнения этой команды.", ephemeral=True)

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.critical(f'❌ Ошибка при запуске бота: {str(e)}')
