import json
import os
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.db_file = config.DB_FILE
        self.data = self.load_data()
        self._create_directory()

    def _create_directory(self):
        """Создает директорию для файла БД, если её нет"""
        directory = os.path.dirname(self.db_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def load_data(self):
        """Загружает данные из JSON-файла"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Ошибка при загрузке данных: {str(e)}")
            return {}

    def save_data(self):
        """Сохраняет данные в JSON-файл"""
        try:
            self._create_directory()
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при сохранении данных: {str(e)}")

    def user_exists(self, user_id):
        """Проверяет существование пользователя"""
        return str(user_id) in self.data

    def get_user(self, user_id):
        """Получает данные пользователя"""
        try:
            user_id = str(user_id)
            if user_id not in self.data:
                self.data[user_id] = {
                    'nickname': '',
                    'position': '',
                    'joined_at': datetime.now().strftime('%d.%m.%Y'),
                    'xp': 0,
                    'description': "",  # Исправлено опечатка в 'description'
                    'level': 1
                }
                self.save_data()
            return self.data[user_id]  # Явно возвращаем словарь
        except Exception as e:
            print(f"Ошибка при получении данных пользователя: {str(e)}")
            return {}  # Возвращаем пустой словарь, а не None

    def update_user(self, user_id, **kwargs):
        """Обновляет данные пользователя с сохранением position"""
        try:
            user = self.get_user(user_id)
            
            # Сохраняем текущее значение position, если оно не передано
            if 'position' not in kwargs:
                kwargs['position'] = user.get('position', '')
            
            # Проверки на корректность данных
            if 'xp' in kwargs and kwargs['xp'] < 0:
                raise ValueError("Опыт не может быть отрицательным")
            if 'level' in kwargs and kwargs['level'] < 1:
                raise ValueError("Уровень не может быть меньше 1")
            
            user.update(kwargs)
            self.save_data()
        except Exception as e:
            print(f"Ошибка при обновлении данных пользователя: {str(e)}")

    def add_xp(self, user_id, amount):
        """Добавляет опыт пользователю"""
        try:
            if amount < 0:
                raise ValueError("Количество опыта не может быть отрицательным")
            
            user = self.get_user(user_id)
            user['xp'] += amount
            self.calculate_level(user)
            self.save_data()
            print(f"Добавлено {amount} XP пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка при добавлении опыта: {str(e)}")

    def calculate_level(self, user):
        """Рассчитывает уровень пользователя"""
        try:
            current_level = user['level']
            while True:
                required_xp = config.LEVEL_MULTIPLIER * current_level ** 2
                if user['xp'] < required_xp:
                    break
                current_level += 1
            
            if current_level != user['level']:
                user['level'] = current_level
                print(f"Уровень повышен до {current_level}")
        except Exception as e:
            print(f"Ошибка при расчете уровня: {str(e)}")

    def refresh(self, user_id=None):
        """Перезагружает данные из файла. 
        Если указан user_id, перезагружает только данные конкретного пользователя"""
        try:
            self.data = self.load_data()
            if user_id:
                # Если указан конкретный пользователь, проверяем его существование
                if str(user_id) not in self.data:
                    # Если пользователя нет в базе, создаем пустую запись
                    self.get_user(user_id)  # Используем get_user для создания профиля
                print(f"Данные пользователя {user_id} успешно обновлены")
            else:
                print("Все данные базы данных успешно обновлены")
        except Exception as e:
            print(f"Ошибка при обновлении данных: {str(e)}")

    def delete_user(self, user_id):
        """Удаляет пользователя из базы"""
        try:
            user_id = str(user_id)
            if user_id in self.data:
                del self.data[user_id]
                self.save_data()
                print(f"Пользователь {user_id} удален")
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {str(e)}")

    def get_all_users(self):
        """Возвращает всех пользователей"""
        return self.data

    def __del__(self):
        """Сохраняет данные при уничтожении объекта"""
        self.save_data()
