# config.py

# 🔑 Базовые настройки
PREFIX = "."  # Префикс команд

# 🔄 Каналы
VERIFICATION_CHANNEL_ID = 1255217613643059270  # Канал верификации
WELCOME_CHANNEL_ID = 1255217613643059270   # Канал приветствия
LEADERBOARD_CHANNEL_ID = 1510310805353009183  # Канал таблицы лидеров
LOG_CHANNEL_ID = 1255221212519596184       # Канал логов

# 🎯 Роли
GUEST_ROLE_ID = 1510307677409120256        # Роль "Гость"
MEMBER_ROLE_ID = 1493217622123352134         # Роль "Участник клана"

# 📊 Система уровней
DB_FILE = '/app/data/database.json'  # Файл базы данных
XP_PER_MESSAGE = 5  # Опыт за сообщение
LEVEL_MULTIPLIER = 100  # Множитель уровня

# 🎯 Тиры профиля
TIER_ROLES = {
    1492100129342357534: "🚫 Outside Tier",  # Outside Tier
    1510308913105469692: "🚫 Outside Tier",  # Outside Tier
    1493218079528976414: "🏅 1 Tier",        # 1 Tier
    1493217898548822056: "🎯 2 Tier",        # 2 Tier
    1493217622123352134: "🎖 3 Tier"         # 3 Tier
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
