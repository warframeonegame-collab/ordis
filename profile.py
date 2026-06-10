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
        self.excluded_commands = ['profile', 'help', 'setprofile', 'setsubdivision', 'updatetable']
        self.forbidden_channels = [
            1257267587432058993,  # ID первого запрещенного канала
            1501029076478201896, # ID второго запрещенного канала
            1498928154415468584,
            1494776417546666106,
            1494765342369517568
        ]
        self._command_cache = {}  # Кэш для предотвращения повторного выполнения команд
        self._cache_ttl = 2.0  # Время жизни кэша (сек)
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

    # Предотвращение повторного выполнения одной и той же команды
    async def _check_duplicate_command(self, ctx) -> bool:
        now = datetime.now().timestamp()
        key = f"{ctx.command.name}:{ctx.message.id}:{ctx.author.id}"
        if key in self._command_cache:
            if now - self._command_cache[key] < self._cache_ttl:
                return True  # Это дубликат
        self._command_cache[key] = now
        # Очистка старых записей
        for k in list(self._command_cache.keys()):
            if now - self._command_cache[k] > self._cache_ttl:
                del self._command_cache[k]
        return False

    # Метод, который будет выполняться перед каждой командой
    async def cog_before_invoke(self, ctx):
        if ctx.channel.id in self.forbidden_channels:
            return False
        # Проверка на дубликат команды
        if await self._check_duplicate_command(ctx):
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

        # Текущий опыт, необходимый для текущего уровня
        current_level_xp_cap = config.LEVEL_MULTIPLIER * user['level'] ** 2
        # Опыт внутри текущего уровня (если уровень > 1, вычитаем опыт предыдущего уровня)
        xp_into_level = user['xp']
        # Сколько опыта нужно для следующего уровня
        next_level_xp = config.LEVEL_MULTIPLIER * (user['level'] + 1) ** 2
        remaining_xp = next_level_xp - xp_into_level

        embed = discord.Embed(
            title=f"Профиль {member.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Запрошено {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        embed.add_field(name="📋 Никнейм", value=user['nickname'] or member.display_name, inline=False)
        embed.add_field(name="🥉 Тир", value=user_tier, inline=False)
        user_data = self.db.get_user(member.id)
        if user.get('position'):
            embed.add_field(name="🏷️ Должность", value=user['position'], inline=False)
        if user.get('subdivision'):
            embed.add_field(name="📁 Подразделение", value=user['subdivision'], inline=False)

        embed.add_field(
            name="📅 Дата вступления", 
            value=f"{user['joined_at']}\n"
                  f"🏆 Уровень: {user['level']}",
            inline=False
        )

        # Прогресс бар
        xp_bar = "█" * int((xp_into_level / current_level_xp_cap) * 20)
        embed.add_field(name="🎯 Прогресс уровня", value=f"{xp_bar}", inline=False)
        embed.add_field(
            name="📊 До следующего уровня", 
            value=f"Осталось {remaining_xp} XP",
            inline=False
        )
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
            admin_cmds = (
                "**Управление пользователями:**\n"
                "`.setprofile @user --position \"текст\"` - полная настройка профиля\n"
                "`.setprofile @user --level N` - установить уровень\n"
                "`.setprofile @user --xp N` - установить опыт\n"
                "**Система:**\n"
                "`.updatetable` - обновить таблицу лидеров"
            )
            embed.add_field(
                name="🛠️ Административные команды",
                value=admin_cmds,
                inline=False
            )
        
        # Команду setsubdivision видят только роль 1493218079528976414 и администраторы
        if discord.utils.get(ctx.author.roles, id=config.SUBDIVISION_ROLE_ID) or ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="📁 Управление подразделениями",
                value="`.setsubdivision @user <название>` - установить подразделение",
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

    @commands.command(name="setprofile")
    @commands.has_permissions(administrator=True)
    async def setprofile(self, ctx, member: discord.Member, *, args: str = ""):
        """Устанавливает профиль пользователя.
        Формат: .setprofile @user --position "текст" --level 5 --xp 100 --subdivision "название" """
        try:
            await ctx.message.delete()
            
            if not args:
                await ctx.send("Укажите хотя бы один параметр. Формат: `.setprofile @user --position \"текст\" --level 5 --xp 100 --subdivision \"название\"`", ephemeral=True, delete_after=10)
                return
            
            import re
            update_data = {}
            
            # --position "текст в кавычках"
            pos_match = re.search(r'--position\s+"([^"]*)"', args)
            if pos_match:
                update_data['position'] = pos_match.group(1)
            
            # --subdivision "текст в кавычках"
            sub_match = re.search(r'--subdivision\s+"([^"]*)"', args)
            if sub_match:
                update_data['subdivision'] = sub_match.group(1)
            
            # --level число
            lvl_match = re.search(r'--level\s+(\d+)', args)
            if lvl_match:
                level = int(lvl_match.group(1))
                if level < 1:
                    raise ValueError("Уровень не может быть меньше 1")
                update_data['level'] = level
            
            # --xp число
            xp_match = re.search(r'--xp\s+(\d+)', args)
            if xp_match:
                xp_val = int(xp_match.group(1))
                if xp_val < 0:
                    raise ValueError("Опыт не может быть отрицательным")
                update_data['xp'] = xp_val
            
            if not update_data:
                await ctx.send("Не распознаны параметры. Используйте: `--position \"текст\"`, `--subdivision \"текст\"`, `--level число`, `--xp число`", ephemeral=True, delete_after=10)
                return
            
            # Автоматически пересчитываем уровень, если задан только xp
            if 'xp' in update_data and 'level' not in update_data:
                temp_xp = update_data['xp']
                new_level = 1
                while True:
                    required = config.LEVEL_MULTIPLIER * new_level ** 2
                    if temp_xp < required:
                        break
                    new_level += 1
                update_data['level'] = new_level
            
            self.db.update_user(member.id, **update_data)
            
            parts = []
            if 'position' in update_data:
                parts.append(f"должность → {update_data['position']}")
            if 'subdivision' in update_data:
                parts.append(f"подразделение → {update_data['subdivision']}")
            if 'level' in update_data:
                parts.append(f"уровень → {update_data['level']}")
            if 'xp' in update_data:
                parts.append(f"опыт → {update_data['xp']}")
            
            await ctx.send(f"✅ Профиль {member.name} обновлён: {', '.join(parts)}", ephemeral=True, delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {str(e)}")

    @commands.command(name="setsubdivision")
    async def setsubdivision(self, ctx, member: discord.Member, *, subdivision: str):
        """Устанавливает подразделение пользователю (только для ролей с правом назначения)."""
        try:
            await ctx.message.delete()
            
            # Проверяем роль или права администратора
            has_permission = discord.utils.get(ctx.author.roles, id=config.SUBDIVISION_ROLE_ID) is not None or ctx.author.guild_permissions.administrator
            
            if not has_permission:
                await ctx.send("❌ У вас нет прав для использования этой команды.", ephemeral=True, delete_after=10)
                return
            
            if not subdivision.strip():
                await ctx.send("❌ Название подразделения не может быть пустым.", ephemeral=True, delete_after=5)
                return
            
            self.db.update_user(member.id, subdivision=subdivision.strip())
            await ctx.send(f"✅ Подразделение для {member.name} установлено: {subdivision}", ephemeral=True, delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Ошибка при установке подразделения: {str(e)}")


# --- Система уровней (ОПЦИОНАЛЬНО) ---

class LevelingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.forbidden_channels = [
            1509113757077475360,
            1509116456896434247
        ]
        self.excluded_commands = ['profile', 'help', 'setprofile', 'setsubdivision', 'setlvl', 'updatetable']

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
            old_level = user_data['level']
            
            self.db.add_xp(user_id, amount)
            
            new_level = self.db.get_user(user_id)['level']
            if new_level > old_level:
                await self._notify_level_up(user_id, new_level)
        except Exception as e:
            print(f"Ошибка при добавлении опыта: {str(e)}")

    async def _notify_level_up(self, user_id, new_level):
        try:
            member = self.bot.get_user(user_id)
            if member:
                await member.send(f"Поздравляем! Вы поднялись на уровень {new_level}!")
                
            leaderboard_channel = self.bot.get_channel(config.LEADERBOARD_CHANNEL_ID)
            if leaderboard_channel:
                await leaderboard_channel.send(f"🎉 {member.mention} поднялся на уровень {new_level}!")
        except Exception as e:
            print(f"Ошибка при уведомлении о повышении уровня: {str(e)}")

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

