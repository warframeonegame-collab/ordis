import discord
from discord.ext import commands
import config
from utils.database import Database
from datetime import datetime
import random

class ProfileSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.excluded_commands = ['profile', 'help', 'setprofile', 'updatetable']
        self.forbidden_channels = [
            1257267587432058993,  # ID первого запрещенного канала
            1501029076478201896, # ID второго запрещенного канала
            1498928154415468584,
            1494776417546666106,
            1494765342369517568
        ]
        self.bot_profile = {
            'nickname': '🤖 Ордис [ERROR_404]',
            'position': 'В процессе... [LOADING...]',
            'joined_at': datetime.now().strftime('%d.%m.%Y'),
            'xp': "∞ [OVERLOW_ERROR]",
            'level': 1,
            'description': (
                'Я ваш помощник и администратор сервера!\n'
                '⚠️ Система работает в режиме отладки...\n'
                '⚠️ Система работает в режиме отладки...\n'
                '🛠️ Процессы инициализации: 75%\n'
                '🔍 База данных: CHECKING...\n'
                '📊 Статистика: UPDATING...'
            ),
            'features': [
       'Моментальная реакция на команды [BUGGED]',
        'Бесконечный запас энергии [OVERLOAD]',
        'Абсолютная память [LOADING...]',
        'Непревзойденная точность [CALIBRATING]',
        'Секретный режим разработчика [UNLOCK WITH BOOST]',
        'Расширенная аналитика клана [UNLOCK WITH BOOST]',
        'Прогнозирование событий [UNLOCK WITH BOOST]',
        'Автоматическое исправление багов [UNLOCK WITH BOOST]'
    ]
}

    # Метод, который будет выполняться перед каждой командой
    async def cog_before_invoke(self, ctx):
        if ctx.channel.id in self.forbidden_channels:
            return False

    # --- Логика профиля (РАБОТАЕТ ВСЕГДА) ---

    @commands.command(name="profile")
    async def profile(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        if member.id == self.bot.user.id:  # Проверка на профиль бота
            return await self.show_bot_profile(ctx)

        try:
            self.db.refresh(member.id)
            user = self.db.get_user(member.id)
            
            if not user:
                await ctx.send("Пользователь не найден в базе данных")
                return

        except Exception as e:
            await ctx.send(f"Ошибка при получении данных профиля: {str(e)}")
            return


        # Определяем текущий Tier пользователя по ID роли
        user_tier = "Не назначен"
        for role_id, display_name in config.TIER_ROLES.items():
            if discord.utils.get(member.roles, id=role_id):
                user_tier = display_name
                break

        # Рассчитываем необходимый опыт до следующего уровня (только для отображения)
        required_xp = config.LEVEL_MULTIPLIER * (user['level'] + 1)**2 - user['xp']

        embed = discord.Embed(
            title=f"Профиль {member.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Запрошено {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        embed.add_field(name="📋 Никнейм", value=user['nickname'] or member.display_name, inline=False)
        embed.add_field(name="🥉 Тир", value=user_tier, inline=False)
        user_data = self.db.get_user(member.id)
        if 'position' in user_data:
            embed.add_field(name="🏷️ Должность", value=user['position'], inline=False)

        embed.add_field(
            name="📅 Дата вступления", 
            value=f"{user['joined_at']}\n"
                  f"🏆 Уровень: {user['level']}\n"
                  f"🎯 Опыт: {user['xp']}/{required_xp}",
            inline=False
        )

        # Прогресс бар
        xp_bar = "█" * int((user['xp'] / (config.LEVEL_MULTIPLIER * user['level']**2)) * 20)
        embed.add_field(name="🎯 Прогресс уровня", value=f"{xp_bar}", inline=False)
        await ctx.message.delete()
        await ctx.send(embed=embed, delete_after=60)

    async def show_bot_profile(self, ctx):
        embed = discord.Embed(
            title=self.bot_profile['nickname'],
            description=self.bot_profile['description'],
            color=discord.Color.green()  # Зеленый цвет для бота
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        embed.add_field(
            name="🎯 Статус", 
            value=self.bot_profile['position'], 
            inline=False
        )
        
        embed.add_field(
            name="📅 Дата создания", 
            value=self.bot_profile['joined_at'], 
            inline=True
        )
        
        embed.add_field(
            name="🌟 Уровень", 
            value=self.bot_profile['level'], 
            inline=True
        )
        
        embed.add_field(
            name="⭐ Опыт", 
            value=self.bot_profile['xp'], 
            inline=True
        )
        
        embed.add_field(
            name="Возможности", 
            value="\n".join(self.bot_profile['features']), 
            inline=False
        )
        
        await ctx.message.delete()
        await ctx.send(embed=embed, delete_after=60)


    async def force_update_user_data(self, user_id):
        try:
            # Проверяем существование пользователя
            if not self.db.user_exists(user_id):
                # Создаем нового пользователя
                self.db.create_user(user_id, {
                    'nickname': '',
                    'position': '',
                    'joined_at': datetime.now().strftime('%d.%m.%Y'),
                    'xp': 0,
                    'level': 1
                })
            
            # Обновляем данные пользователя
            user = self.db.get_user(user_id)
            # Здесь можно добавить дополнительную логику обновления
            self.db.save_data()
            
        except Exception as e:
            print(f"Ошибка при принудительном обновлении данных пользователя: {str(e)}")
    # --- Административные команды (РАБОТАЮТ ВСЕГДА) ---
    @commands.command(name="help")
    async def help_command(self, ctx):
        # Создаем основной embed
        embed = discord.Embed(
            title="📣 Система помощи",
            description="Список доступных команд",
            color=discord.Color.blue()
        )
        
        # Базовые команды для всех
        embed.add_field(
            name="🔍 Основные команды",
            value=(
                "`.profile` - просмотр вашего профиля\n"
                "`.help` - показать это сообщение\n"
            ),
            inline=False
        )

        # Проверяем права администратора
        if ctx.author.guild_permissions.administrator:
            # Добавляем раздел для администраторов
            embed.add_field(
                name="🛠️ Административные команды",
                value=(
                    "**Управление пользователями:**\n"
                    "`.setposition <пользователь>` - изменение должности\n"
                    "**Система:**\n"
                    "`.updatetable` - обновить таблицу лидеров"
                ),
                inline=False
            )

        # Добавляем футер
        embed.set_footer(text="Для использования команд введите префикс '.' перед командой")
        try:
            await ctx.message.delete()  # Удаляем сообщение пользователя
            await ctx.send(embed=embed, delete_after=60)
        except discord.Forbidden:
            await ctx.send("У меня нет прав на удаление сообщений!", delete_after=20)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {str(e)}")

    @commands.command(name="setper")
    @commands.has_permissions(administrator=True)
    async def setper(self, ctx, member: discord.Member, *, position):
        try:
            await ctx.message.delete()
            self.db.update_user(member.id, position=position)
            await ctx.send(f"Должность для {member.name} установлена: {position}", ephemeral=True, delete_after=5)
        except Exception as e:
            await ctx.send(f"Ошибка при установке должности: {str(e)}")





# --- Система уровней (ОПЦИОНАЛЬНО) ---

class LevelingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.forbidden_channels = [
            1509113757077475360,
            1509116456896434247
        ]
        self.excluded_commands = ['profile', 'help', 'setper', 'setlvl', 'updatetable']

    def calculate_random_xp(self, message):
        # Базовый диапазон опыта
        base_min = config.XP_PER_MESSAGE - 2
        base_max = config.XP_PER_MESSAGE + 2
        
        # Случайное базовое значение
        base_xp = random.randint(base_min, base_max)
        
        # Бонусы
        if len(message.content) > 100:
            base_xp += random.randint(3, 7)  # случайный бонус за длинное сообщение
        if message.mentions:
            base_xp += random.randint(1, 3)  # случайный бонус за упоминания
        
        return base_xp

    async def add_experience(self, user_id, amount):
        try:
            user_data = self.db.get_user(user_id)
            new_xp = user_data['xp'] + amount
            self.db.update_user(user_id, xp=new_xp)
            await self.check_level_up(user_id, new_xp)
        except Exception as e:
            print(f"Ошибка при добавлении опыта: {str(e)}")

    async def check_level_up(self, user_id, xp):
        try:
            user_data = self.db.get_user(user_id)
            current_level = user_data['level']
            
            required_xp = config.LEVEL_MULTIPLIER * (current_level + 1)**2
            
            if xp >= required_xp:
                new_level = current_level + 1
                self.db.update_user(user_id, level=new_level)
                member = self.bot.get_user(user_id)
                if member:
                    await member.send(f"Поздравляем! Вы поднялись на уровень {new_level}!")
                    
                leaderboard_channel = self.bot.get_channel(config.LEADERBOARD_CHANNEL_ID)
                if leaderboard_channel:
                    await leaderboard_channel.send(f"🎉 {member.mention} поднялся на уровень {new_level}!")
                    
        except Exception as e:
            print(f"Ошибка при проверке уровня: {str(e)}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id in self.forbidden_channels:
            return

        # Проверяем, является ли сообщение командой
        if message.content.startswith(self.bot.command_prefix):
            command_name = message.content.split()[0].split(self.bot.command_prefix)[1]
            if command_name in self.excluded_commands:
                return

        # Получаем случайное значение опыта
        random_xp = self.calculate_random_xp(message)
        await self.add_experience(message.author.id, random_xp)
# Функция для загрузки когов
async def setup(bot):
    try:
        # Обязательно загружаем систему профилей
        await bot.add_cog(ProfileSystem(bot))
        
        # Опционально загружаем систему уровней
        # Если хотите отключить уровни - просто закомментируйте следующую строку
        await bot.add_cog(LevelingSystem(bot))
        
    except Exception as e:
        print(f"Ошибка при загрузке когов: {str(e)}")

