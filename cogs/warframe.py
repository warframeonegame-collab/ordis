import discord
from discord.ext import commands, tasks
import httpx
import logging
import asyncio
from datetime import datetime, timezone

WARFRAME_API = "https://api.warframestat.us/pc/"
WARFRAME_COLOR = discord.Color.from_rgb(255, 185, 15)

BARO_NOTIFY_CHANNEL_ID = 1255444820902543380
WARFRAME_INFO_CHANNEL_ID = 1514184364941119528

CYCLE_TRANSLATIONS = {
    "day": "День",
    "night": "Ночь",
    "warm": "Тепло",
    "cold": "Холод",
    "fass": "Фэз",
    "vome": "Воум",
}

BARO_ITEM_TRANSLATIONS = {
    "Braton Prime Set": "Набор Братон Прайм",
    "Saryn Prime Set": "Набор Сарин Прайм",
    "Lex Prime Set": "Набор Лекс Прайм",
    "Mag Prime Set": "Набор Маг Прайм",
    "Frost Prime Set": "Набор Фрост Прайм",
    "Ember Prime Set": "Набор Эмбер Прайм",
    "Nova Prime Set": "Набор Нова Прайм",
    "Boltor Prime Set": "Набор Болтор Прайм",
    "Fragor Prime Set": "Набор Фрагор Прайм",
    "Dakka Prime Set": "Набор Дакка Прайм",
    "Nikana Prime Set": "Набор Никана Прайм",
    "Venka Prime Set": "Набор Венка Прайм",
    "Cernos Prime Set": "Набор Цернос Прайм",
    "Galatine Prime Set": "Набор Галатин Прайм",
    "Tigris Prime Set": "Набор Тигрис Прайм",
    "Orthos Prime Set": "Набор Ортос Прайм",
    "Kamas Prime Set": "Набор Камас Прайм",
    "Akstiletto Prime Set": "Набор Акстилетто Прайм",
    "Spira Prime Set": "Набор Спира Прайм",
    "Kavasa Prime Kubrow Collar Set": "Набор Каваса Прайм",
    "Primed Continuity": "Основная Непрерывность Прайм",
    "Primed Flow": "Основной Поток Прайм",
    "Primed Cryo Rounds": "Основные Крио Снаряды Прайм",
    "Primed Pistol Gambit": "Основной Пистолетный Гамбит Прайм",
    "Primed Target Cracker": "Основной Целевой Кракер Прайм",
    "Primed Ravage": "Основное Разрушение Прайм",
    "Primed Chamber": "Основная Камера Прайм",
    "Primed Firestorm": "Основной Огненный Шторм Прайм",
    "Primed Fever Strike": "Основной Лихорадочный Удар Прайм",
    "Primed Convulsion": "Основной Судорога Прайм",
    "Primed Expel": "Основное Изгнание Прайм",
    "Primed Bane": "Основное Проклятие Прайм",
    "Primed Sure Footed": "Основная Уверенная Стопа Прайм",
    "Primed Animal Instinct": "Основной Животный Инстинкт Прайм",
    "Primed Pack Leader": "Основной Вожак Стая Прайм",
    "Primed Reach": "Основная Досягаемость Прайм",
    "Primed Point Blank": "Основное Точное Попадание Прайм",
    "Primed Pressure Point": "Основное Боевое Давление Прайм",
    "Primed Regen": "Основная Регенерация Прайм",
    "Primed Scorch": "Основной Обжиг Прайм",
    "Primed Smite": "Основное Поражение Прайм",
    "Prisma Skana": "Призма Скана",
    "Prisma Dual Cleavers": "Призма Двойные Клинки",
    "Prisma Gorgon": "Призма Горгон",
    "Prisma Machete": "Призма Мачете",
    "Prova Vandal": "Прова Вандал",
    "Dera Vandal": "Дера Вандал",
    "Strun Vandal": "Струн Вандал",
    "Karak Wraith": "Карак Рэт",
    "Tenet Diplos": "Тенет Диплос",
    "Tenet Envoy": "Тенет Энвой",
    "Tenet Ferrox": "Тенет Феррокс",
    "Tenet Flux": "Тенет Флукс",
    "Tenet Grigori": "Тенет Григори",
    "Tenet Livia": "Тенет Ливия",
    "Tenet Spirex": "Тенет Спайрекс",
    "Tenet Tetra": "Тенет Тетра",
    "Tenet Exec": "Тенет Экзек",
    "Tenet Plinx": "Тенет Плинкс",
    "Kuva Chakkhurr": "Кува Чакхурр",
    "Kuva Bramma": "Кува Брамма",
    "Kuva Ogris": "Кува Огрис",
    "Kuva Karak": "Кува Карак",
    "Kuva Hind": "Кува Хинд",
    "Kuva Shildeg": "Кува Шилдег",
    "Kuva Seer": "Кува Сир",
    "Kuva Quartakk": "Кува Квартакк",
    "Kuva Kohm": "Кува Коум",
    "Kuva Kraken": "Кува Кракен",
    "Kuva Tonkor": "Кува Тонкор",
    "Kuva Brakk": "Кува Бракк",
    "Kuva Sobek": "Кува Собек",
    "KuvaZarr": "Кува Зарр",
    "KuvaAyanga": "Кува Аянга",
    "Arcane Energize": "Аркан Энергиз",
    "Arcane Grace": "Аркан Грейс",
    "Arcane Guardian": "Аркан Гардиан",
    "Arcane Strike": "Аркан Удар",
    "Arcane Velocity": "Аркан Скорость",
    "Arcane Agility": "Аркан Ловкость",
    "Arcane Precision": "Аркан Точность",
    "Arcane Momentum": "Аркан Импульс",
    "Arcane Rage": "Аркан Ярость",
    "Arcane Avenger": "Аркан Мститель",
    "Arcane Ultimatum": "Аркан Ультиматум",
    "Arcane Phoenix": "Аркан Феникс",
    "Noggle Statue - Teshin": "Статуэтка Ноггл - Тешин",
    "Orokin Tea Set": "Орокин Чайный Набор",
    "Crania Ephemera": "Эфемера Крания",
    "Trio Orbit Ephermera": "Эфемера Трио Орбит",
    "Veiled Riven Cipher": "Туманный Ривен Шифр",
    "Exilus Warframe Adapter": "Экзилус Адаптер Варфрейма",
    "Exilus Weapon Adapter Blueprint": "Чертёж Экзилус Адаптера Оружия",
    "Detonite Ampule": "Ампула Детонита",
    "Fieldron Sample": "Образец Филдрона",
    "Mutagen Mass": "Мутагенная Масса",
    "Stance Forma Blueprint": "Чертёж Стансы Форма",
    "Relic Pack": "Набор Реликтов",
    "Primary Arcane Adapter": "Адаптер Аркана Основного",
    "Secondary Arcane Adapter": "Адаптер Аркана Дополнительного",
    "10k Kuva": "10к Кува",
    "50,000 Kuva": "50 000 Кува",
    "30,000 Endo": "30 000 Эндо",
    "3x Forma": "3x Форма",
    "Umbra Forma Blueprint": "Чертёж Умбра Форма",
    "Kitgun Riven Mod": "Мод Ривен Китган",
    "Zaw Riven Mod": "Мод Ривен Зау",
    "Rifle Riven Mod": "Мод Ривен Винтовки",
    "Shotgun Riven Mod": "Мод Ривен Дробовика",
    "Counterbalance": "Противовес",
    "Gauss in Action Glyph": "Глиф Гаусс в Действии",
    "Grendel in Action Glyph": "Глиф Грендель в Действии",
    "Protea in Action Glyph": "Глиф Протея в Действии",
    "Xaku in Action Glyph": "Глиф Ксату в Действии",
    "Bishamo Pauldrons Blueprint": "Чертёж Наплечники Бишамо",
    "Bishamo Cuirass Blueprint": "Чертёж Куярасс Бишамо",
    "Bishamo Helmet Blueprint": "Чертёж Шлем Бишамо",
    "Bishamo Greaves Blueprint": "Чертёж Поножи Бишамо",
}


async def fetch_warframe_data(retries=3):
    """Получает данные Warframe API с повторными попытками."""
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.get(WARFRAME_API, headers={"User-Agent": "OrdisBot/1.0"})
                r.raise_for_status()
                return r.json()
        except httpx.ReadTimeout:
            print(f"[Warframe] API таймаут (попытка {attempt + 1}/{retries})")
            if attempt < retries - 1:
                import asyncio as _aio
                await _aio.sleep(5)
            else:
                raise


def translate_item(name):
    return BARO_ITEM_TRANSLATIONS.get(name, name)


class Warframe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._baro_notified = False
        self._message_ids = {}
        print("[Warframe] Ког инициализирован")

    @commands.Cog.listener()
    async def on_ready(self):
        print("[Warframe] on_ready сработал, запуск обновления...")
        try:
            data = await fetch_warframe_data()
            print(f"[Warframe] API отвечает, каналы: info={WARFRAME_INFO_CHANNEL_ID}, baro={BARO_NOTIFY_CHANNEL_ID}")
            info_channel = self.bot.get_channel(WARFRAME_INFO_CHANNEL_ID)
            print(f"[Warframe] Канал таймеров найден: {info_channel is not None}")
            if info_channel:
                await self._handle_baro(data.get("voidTrader", {}), info_channel)
                await self._update_cycles(data, info_channel)
                print("[Warframe] Начальное обновление выполнено!")
            else:
                print(f"[Warframe] ОШИБКА: Канал {WARFRAME_INFO_CHANNEL_ID} не найден!")
            # Запускаем цикл обновлений
            if not self.warframe_update_loop.is_running():
                self.warframe_update_loop.start()
                print("[Warframe] Цикл обновлений запущ!")
        except Exception as e:
            print(f"[Warframe] ОШИБКА: {e}")
            import traceback
            traceback.print_exc()

    # ==================== ЦИКЛ ====================

    @tasks.loop(minutes=5)
    async def warframe_update_loop(self):
        try:
            data = await fetch_warframe_data()
        except Exception as e:
            logging.error(f"[Warframe] Ошибка API: {e}")
            return

        info_channel = self.bot.get_channel(WARFRAME_INFO_CHANNEL_ID)
        if not info_channel:
            logging.warning("[Warframe] Канал таймеров не найден!")
            return

        await self._handle_baro(data.get("voidTrader", {}), info_channel)
        await self._update_cycles(data, info_channel)

    @warframe_update_loop.before_loop
    async def before_warframe_loop(self):
        await self.bot.wait_until_ready()

    @warframe_update_loop.error
    async def warframe_loop_error(self, error):
        logging.error(f"[Warframe] Ошибка в цикле: {error}")


    # ==================== БАРО КИ'ТИР ====================

    async def _handle_baro(self, vt, info_channel):
        if not vt:
            return

        now = datetime.now(timezone.utc)
        activation = vt.get("activation", "")
        expiry = vt.get("expiry", "")
        location = vt.get("location", "Неизвестно")
        inventory = vt.get("inventory", [])

        is_here = False
        if activation:
            try:
                act_dt = datetime.fromisoformat(activation.replace("Z", "+00:00"))
                is_here = now >= act_dt
            except Exception:
                pass

        if is_here and inventory and not self._baro_notified:
            self._baro_notified = True
            notify_channel = self.bot.get_channel(BARO_NOTIFY_CHANNEL_ID)
            if notify_channel:
                items_text = []
                for item in inventory:
                    name = translate_item(item.get("item", "?"))
                    ducats = item.get("ducats", 0)
                    credits = item.get("credits", 0)
                    items_text.append(f"• **{name}** — <:OldDucats:1512114394094502050> {ducats} | <:Credits:1514175092035424319> {credits}")
                desc = "\n".join(items_text[:20])
                if len(items_text) > 20:
                    desc += f"\n... и ещё {len(items_text) - 20}"
                embed = discord.Embed(
                    title="🛒 Баро Ки'Тир прибыл!",
                    description=desc,
                    color=WARFRAME_COLOR,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="📍 Локация", value=location, inline=True)
                if expiry:
                    try:
                        exp_dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                        diff = exp_dt - now
                        hours = int(diff.total_seconds() // 3600)
                        mins = int((diff.total_seconds() % 3600) // 60)
                        embed.add_field(name="⏳ Улетает через", value=f"~{hours}ч {mins}м", inline=True)
                    except Exception:
                        pass
                embed.set_footer(text="Данные с warframestat.us")
                await notify_channel.send(embed=embed)

        if not is_here and self._baro_notified:
            self._baro_notified = False

        now = datetime.now(timezone.utc)
        timer_lines = []

        if not is_here and activation:
            try:
                act_dt = datetime.fromisoformat(activation.replace("Z", "+00:00"))
                diff = act_dt - now
                if diff.total_seconds() > 0:
                    days = int(diff.total_seconds() // 86400)
                    hours = int((diff.total_seconds() % 86400) // 3600)
                    mins = int((diff.total_seconds() % 3600) // 60)
                    timer_lines.append(f"🕐 **Баро Ки'Тир** прибудет через: **{days}д {hours}ч {mins}м**")
                else:
                    timer_lines.append("🕐 **Баро Ки'Тир** только что прибыл!")
            except Exception:
                pass
        elif is_here and expiry:
            try:
                exp_dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                diff = exp_dt - now
                if diff.total_seconds() > 0:
                    hours = int(diff.total_seconds() // 3600)
                    mins = int((diff.total_seconds() % 3600) // 60)
                    timer_lines.append(f"🕐 **Баро Ки'Тир** улетает через: **{hours}ч {mins}м**")
                else:
                    timer_lines.append("🕐 **Баро Ки'Тир** улетел!")
            except Exception:
                pass

        if timer_lines:
            baro_embed = discord.Embed(
                title="🕐 Баро Ки'Тиир",
                description="\n".join(timer_lines),
                color=WARFRAME_COLOR,
            )
            baro_embed.add_field(name="📍 Локация", value=location, inline=True)
            await self._publish_embed_to_info_channel(info_channel, "baro", baro_embed)

    # ==================== ФАЗЫ ОТКРЫТОГО МИРА ====================

    async def _update_cycles(self, data, info_channel):
        now = datetime.now(timezone.utc)
        lines = []

        cetus = data.get("cetusCycle", {})
        if cetus:
            state = CYCLE_TRANSLATIONS.get(cetus.get("state", ""), cetus.get("state", "?"))
            emoji = "☀️" if cetus.get("isDay", True) else "🌙"
            try:
                exp_dt = datetime.fromisoformat(cetus.get("expiry", "").replace("Z", "+00:00"))
                diff = exp_dt - now
                total_mins = max(0, int(diff.total_seconds() // 60))
                hours = total_mins // 60
                mins = total_mins % 60
                lines.append(f"{emoji} **Равнины Эйдолона**: {state} (до смены: {hours}ч {mins}м)")
            except Exception:
                lines.append(f"{emoji} **Равнины Эйдолона**: {state}")

        vallis = data.get("vallisCycle", {})
        if vallis:
            state = CYCLE_TRANSLATIONS.get(vallis.get("state", ""), vallis.get("state", "?"))
            emoji = "🔥" if vallis.get("isWarm", False) else "❄️"
            try:
                exp_dt = datetime.fromisoformat(vallis.get("expiry", "").replace("Z", "+00:00"))
                diff = exp_dt - now
                total_mins = max(0, int(diff.total_seconds() // 60))
                hours = total_mins // 60
                mins = total_mins % 60
                lines.append(f"{emoji} **Долина Сфер**: {state} (до смены: {hours}ч {mins}м)")
            except Exception:
                lines.append(f"{emoji} **Долина Сфер**: {state}")

        cambion = data.get("cambionCycle", {})
        if cambion:
            state = CYCLE_TRANSLATIONS.get(cambion.get("state", ""), cambion.get("state", "?"))
            emoji = "🦠" if cambion.get("state", "") == "fass" else "🐛"
            try:
                exp_dt = datetime.fromisoformat(cambion.get("expiry", "").replace("Z", "+00:00"))
                diff = exp_dt - now
                total_mins = max(0, int(diff.total_seconds() // 60))
                hours = total_mins // 60
                mins = total_mins % 60
                lines.append(f"{emoji} **Камбионский Дрейф**: {state} (до смены: {hours}ч {mins}м)")
            except Exception:
                lines.append(f"{emoji} **Камбионский Дрейф**: {state}")

        if lines:
            cycles_embed = discord.Embed(
                title="🌍 Циклы мира",
                description="\n".join(lines),
                color=WARFRAME_COLOR,
                timestamp=datetime.now(timezone.utc)
            )
            cycles_embed.set_footer(text="warframestat.us • обновляется каждые 5 мин")
            await self._publish_embed_to_info_channel(info_channel, "cycles", cycles_embed)

    # ==================== УТИЛИТЫ ====================

    async def _publish_embed_to_info_channel(self, channel, section_key, embed):
        msg_id = self._message_ids.get(section_key)
        if msg_id:
            try:
                msg = await channel.fetch_message(msg_id)
                await msg.edit(embed=embed)
                return
            except (discord.NotFound, discord.HTTPException):
                self._message_ids.pop(section_key, None)
            except Exception as e:
                logging.error(f"[Warframe] Ошибка редактирования {section_key}: {e}")

        try:
            sent = await channel.send(embed=embed)
            self._message_ids[section_key] = sent.id
            logging.info(f"[Warframe] Отправлено '{section_key}' в {channel.name}")
        except Exception as e:
            logging.error(f"[Warframe] Ошибка отправки '{section_key}': {e}")

    # ==================== КОМАНДЫ ====================

    @commands.command(name="testbaro")
    @commands.has_permissions(administrator=True)
    async def test_baro(self, ctx):
        """Тест: отправляет уведомление о приходе Баро Ки'Тира."""
        try:
            await ctx.message.delete()
        except Exception:
            pass

        notify_channel = self.bot.get_channel(BARO_NOTIFY_CHANNEL_ID)
        if not notify_channel:
            await ctx.send("❌ Канал уведомлений не найден!", delete_after=10)
            return

        test_items = [
            ("Набор Братон Прайм", 450, 175000),
            ("Набор Сарин Прайм", 500, 200000),
            ("Основная Непрерывность Прайм", 300, 150000),
            ("Аркан Энергиз", 0, 250000),
            ("Призма Скана", 150, 50000),
            ("Чертёж Умбра Форма", 150, 0),
            ("Туманный Ривен Шифр", 20, 75000),
        ]

        items_text = []
        for name, ducats, credits in test_items:
            items_text.append(f"• **{name}** — <:OldDucats:1512114394094502050> {ducats} | <:Credits:1514175092035424319> {credits}")

        embed = discord.Embed(
            title="🛒 Баро Ки'Тир прибыл! (ТЕСТ)",
            description="\n".join(items_text),
            color=WARFRAME_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="📍 Локация", value="Kronia Relay (Saturn)", inline=True)
        embed.add_field(name="⏳ Улетает через", value="~24ч 0м", inline=True)
        embed.set_footer(text="ТЕСТОВОЕ СООБЩЕНИЕ")

        try:
            await notify_channel.send(embed=embed)
            await ctx.send("✅ Тестовое уведомление Баро отправлено!", delete_after=10)
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}", delete_after=10)

    @commands.command(name="wf")
    async def wf_manual(self, ctx):
        """Принудительно обновляет Warframe-данные."""
        print(f"[Warframe] .wf команда от {ctx.author}")
        try:
            await ctx.message.delete()
        except Exception:
            pass

        try:
            data = await fetch_warframe_data()
            print("[Warframe] .wf: API данные получены")
        except Exception as e:
            print(f"[Warframe] .wf: Ошибка API: {e}")
            await ctx.send(f"❌ Ошибка API: {e}", delete_after=15)
            return

        info_channel = self.bot.get_channel(WARFRAME_INFO_CHANNEL_ID)
        print(f"[Warframe] .wf: Канал найден: {info_channel is not None} (ID: {WARFRAME_INFO_CHANNEL_ID})")
        if info_channel:
            try:
                await self._handle_baro(data.get("voidTrader", {}), info_channel)
                print("[Warframe] .wf: Баро обработан")
            except Exception as e:
                print(f"[Warframe] .wf: Ошибка Баро: {e}")
            try:
                await self._update_cycles(data, info_channel)
                print("[Warframe] .wf: Циклы обработаны")
            except Exception as e:
                print(f"[Warframe] .wf: Ошибка циклов: {e}")
            await ctx.send("✅ Warframe-данные обновлены!", delete_after=10)
        else:
            print(f"[Warframe] .wf: ОШИБКА - Канал {WARFRAME_INFO_CHANNEL_ID} не найден!")
            await ctx.send("❌ Канал таймеров не найден!", delete_after=10)

    @commands.command(name="testwf")
    async def test_wf(self, ctx):
        """Тест: отправляет тестовое сообщение в канал таймеров."""
        info_channel = self.bot.get_channel(WARFRAME_INFO_CHANNEL_ID)
        if not info_channel:
            await ctx.send(f"❌ Канал {WARFRAME_INFO_CHANNEL_ID} не найден!", delete_after=10)
            return
        try:
            msg = await info_channel.send("🔧 Тестовое сообщение от Ордиса...")
            await ctx.send(f"✅ Тестовое сообщение отправлено в {info_channel.mention}!", delete_after=10)
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}", delete_after=10)


async def setup(bot):
    await bot.add_cog(Warframe(bot))