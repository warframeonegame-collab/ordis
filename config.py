# config.py

# 🔑 Базовые настройки
PREFIX = "."  # Префикс команд

# 🔄 Каналы
VERIFICATION_CHANNEL_ID = 1509113757077475360  # Канал верификации
WELCOME_CHANNEL_ID = 1509113757077475360     # Канал приветствия
LEADERBOARD_CHANNEL_ID = 1509114878089105448  # Канал таблицы лидеров
LOG_CHANNEL_ID = 1255221212519596184       # Канал логов

# 🎯 Роли
GUEST_ROLE_ID = 1509127550905876591         # Роль "Гость"
MEMBER_ROLE_ID = 1509129745655402647         # Роль "Участник клана"

# 📊 Система уровней
DB_FILE = 'database.json'  # Файл базы данных
XP_PER_MESSAGE = 5  # Опыт за сообщение
LEVEL_MULTIPLIER = 100  # Множитель уровня

# 🎯 Тиры профиля
TIER_ROLES = {
    1509127807614320751: "🚫 Outside Tier",  # Outside Tier
    1509126425167265792: "🚫 Outside Tier",  # Outside Tier
    1509129884524478505: "🏅 1 Tier",        # 1 Tier
    1509129813997256734: "🎯 2 Tier",        # 2 Tier
    1509129745655402647: "🎖 3 Tier"         # 3 Tier
}

# 📋 Ограничения
NICKNAME_MAX_LENGTH = 24  # Максимальная длина ника


# 📅 Временные настройки
MESSAGE_DELETE_DELAY = 60  # Время удаления сообщений (сек)
HELP_MESSAGE_DELAY = 60    # Время удаления сообщения помощи

# 🔔 Эмодзи
EMOJIS = {
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "🔍"
}
