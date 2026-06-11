# cogs/verification.py

import discord
from discord.ext import commands
import re
from config import VERIFICATION_CHANNEL_ID, WELCOME_CHANNEL_ID, GUEST_ROLE_ID, MEMBER_ROLE_ID, NICKNAME_MAX_LENGTH
from utils.database import Database

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Приветствие нового участника и выдача роли "Гость" при входе."""
        welcome_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        verification_channel = self.bot.get_channel(VERIFICATION_CHANNEL_ID)
        guest_role = member.guild.get_role(GUEST_ROLE_ID)

        if guest_role:
            await member.add_roles(guest_role)

        # Создаём запись пользователя с реальной датой вступления из Discord
        real_joined = member.joined_at.strftime('%d.%m.%Y') if member.joined_at else None
        self.db.get_user(member.id, joined_at=real_joined)

        await welcome_channel.send(
            f"Добро пожаловать, {member.mention}! "
            f"Чтобы стать участником клана, введите свой игровой ник в канале {verification_channel.mention}.", delete_after=30
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        """Обработка сообщения с ником в канале верификации."""
        if message.author == self.bot.user:
            return

        # Проверяем канал
        if message.channel.id == VERIFICATION_CHANNEL_ID:
            # Очищаем чат от старых сообщений (оставляем только последнее)
            await message.channel.purge(limit=100, check=lambda m: m.author != self.bot.user)

            # Валидация ника
            if len(message.content) > NICKNAME_MAX_LENGTH:
                await message.channel.send(f"Ник слишком длинный! Максимум {NICKNAME_MAX_LENGTH} символов.", delete_after=5)
                return

            if not re.match(r'^[a-zA-Z0-9_\-\.\[\] ]+$', message.content):
                await message.channel.send("Ник может содержать только латинские буквы, цифры, символы '_', '-', '.', '[', ']' и пробел.", delete_after=5)
                return

            member = message.author
            guild = message.guild

            # Получаем роли
            guest_role = guild.get_role(GUEST_ROLE_ID)
            member_role = guild.get_role(MEMBER_ROLE_ID)

            # ДИАГНОСТИКА — выводим информацию в консоль
            print(f"\n--- ДИАГНОСТИКА ВЕРИФИКАЦИИ ---")
            print(f"Пользователь: {member.display_name} (ID: {member.id})")
            print(f"Позиция роли пользователя: {member.top_role.position}")
            print(f"Роль пользователя: {member.top_role.name}")
            print(f"Позиция роли бота: {guild.me.top_role.position}")
            print(f"Роль бота: {guild.me.top_role.name}")
            print(f"Права бота: {guild.me.guild_permissions}")

            # ПРОВЕРКА 1: Администратор
            if member.guild_permissions.administrator:
                await message.channel.send(
                    "❌ Бот не может верифицировать пользователей с правами администратора. "
                    "Обратитесь к администрации."
                )
                print("ОШИБКА: Пользователь — администратор")
                return

            # ПРОВЕРКА 2: Иерархия ролей
            if guild.me.top_role.position <= member.top_role.position:
                await message.channel.send(
                    "❌ У бота недостаточно прав для верификации этого пользователя. "
                    "Обратитесь к администратору сервера."
                )
                print("ОШИБКА: Роль бота ниже или равна роли пользователя!")
                return

            # ПРОВЕРКА 3: Существование ролей
            if not guest_role or not member_role:
                await message.channel.send(
                    "❌ Ошибка конфигурации бота. "
                    "Обратитесь к администратору."
                )
                print("ОШИБКА: Одна из ролей не найдена!")
                return

            try:
                # Меняем ник
                await member.edit(nick=message.content)

                # Убираем старую роль
                if guest_role and guest_role in member.roles:
                    await member.remove_roles(guest_role)

                # Выдаём новую роль
                if member_role:
                    await member.add_roles(member_role)

                # УДАЛЕНИЕ СООБЩЕНИЯ С ОБРАБОТКОЙ ОШИБКИ 404
                try:
                    await message.delete()
                except discord.NotFound:
                    pass  # Сообщение уже удалено (ошибка 10008), игнорируем

                # Отправляем подтверждение
                await message.channel.send(f"✅ {member.mention}, ваш ник установлен и вы приняты в клан!", delete_after=30)
                print("ВЕРИФИКАЦИЯ УСПЕШНА")

            except discord.Forbidden as e:
                print(f"ОШИБКА ПРАВ: {e}")
                await message.channel.send(
                    "К сожалению, верификация не прошла из‑за ограничений прав. "
                    "Обратитесь к администратору сервера для решения проблемы."
                )
            except Exception as e:
                print(f"НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
                await message.channel.send(
                    "Произошла непредвиденная ошибка. "
                    "Пожалуйста, попробуйте позже или обратитесь к основателю клана @_poxyi. "
                )

async def setup(bot):
    await bot.add_cog(Verification(bot))
