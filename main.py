import library.my_database as DbClass
import library.game_settings as Config
import telebot
import time
import threading
from telebot import types

WordGenerator = Config.WordGen(Config.dic_path)
Database = DbClass.Database(Config.db_path)
ExecutorBot = None

GameSession = list()
SoloPlay = dict()  # Список игроков и ID игры, в которую играет определнный игрок Соло
SoloGames = dict()  # Словарь из угаданных слов Соло
MessagesSolo = dict()


def console_log(text: str = "Empty log"):
    print(f'[LOG] {text}')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Начать")
markup.add(item1)


def bot_polling():
    global ExecutorBot
    console_log("Бот запустился.")
    while True:
        try:
            console_log("Новая сессия сгенерирована.")
            ExecutorBot = telebot.TeleBot(Config.token, num_threads=30)
            Handler()
            ExecutorBot.polling(none_stop=True, interval=Config.interval_to_response, timeout=Config.timeout)
        except Exception as ex:
            console_log(f"Бот остановлен. Ошибка: {ex}.")
            ExecutorBot.stop_polling()
            time.sleep(Config.timeout)
        else:
            console_log("Бот полностью остановлен.")
            ExecutorBot.stop_polling()
            break




def send_message(chat_id, text: str, disable_ntf: bool = False):
    return ExecutorBot.send_message(chat_id, text, parse_mode='html', disable_notification=disable_ntf,
                                    reply_markup=markup)


def send_sticker(chat_id, stick_id: str):
    return ExecutorBot.send_sticker(chat_id, sticker=stick_id, reply_markup=markup)


def remove_message(chat_id, message_id):
    return ExecutorBot.delete_message(chat_id, message_id)


def welcome_on_server(PlayerID, Message):
    if 'start' in Message:
        send_sticker(PlayerID, 'CAACAgIAAxkBAAEK0zBlY8-TMit9H_quY45jrvG4Xi9k5AACgBMAApRmuEihPFaGjuIpgTME')
        send_message(PlayerID, Config.HelloWorld)
        return
    Message = str(Message.split(' ')[0])
    if (len(Message) > 14) or (len(Message) < 4) or (not (Message.isascii())):
        return send_message(PlayerID, f"""
Прочтите ещё раз правила создания никнейма.
""")
    if (Database.PlayerNickIsUsed(Message)):
        return send_message(PlayerID, Config.ReRead)
    Database.PlayerCreate(PlayerID, Message)
    Player = Database.PlayerGet(PlayerID)
    send_message(PlayerID, f"""
Приветствую, <a href = "tg://user?id={PlayerID}">{Player['nick']}</a> [{Player['id']}]!
Теперь ты один из нас.
""")
    send_sticker(PlayerID, 'CAACAgIAAxkBAAEK00plY-AC8yGS7-qkQnYPpWHyhsKSBQACTyEAAsGPOErFNaTJGRW8-zME')
    console_log(f"Добавлен новый пользователь {Message} | TelegramID: {PlayerID}")
    return


def SoloMode(PlayerID, m_message, MessageID):
    GameSession.append(PlayerID)
    user_player = Database.PlayerGet(PlayerID)
    game_id = SoloPlay[user_player['id']]
    guessed_word = SoloGames[game_id]
    game = Database.get_info(game_id)
    m_message = str(m_message)
    if (len(m_message) != 1) and (len(m_message) != len(game['word'])):
        GameSession.remove(PlayerID)
        return send_message(PlayerID, "❌ Введите одну букву или назовите слово целиком!")
    if (len(m_message) == len(game['word'])):
        m_message = m_message.replace('ё', 'е')
        if m_message.lower() == game['word']:
            SoloGames.pop(game['id'])
            SoloPlay.pop(user_player['id'])
            Database.game_change_status(game['id'], 'played')
            Database.game_change_value(game['id'], 'end_ts', int(time.time()))
            Database.PlayerIncreaseScore(user_player['id'], Database.get_info(game['id'])['attemps'] + 2)
            user_player = Database.PlayerGet(PlayerID)
            send_message(PlayerID, f"""
🥇 Ура! Вы угадали слово и пережили экзамен - <b>{game['word']}</b>.
Ваша жизнь спасена и вы получаете свой заслуженный отл 10. 
Теперь у вас <b>{user_player['score']}</b> очков.
""")
            GameSession.remove(PlayerID)
            return
        for i in (MessagesSolo[game_id]):
            remove_message(PlayerID, i.message_id)
        if game['attemps'] <= 2:
            Database.game_change_value(game['id'], 'attemps', 0)
            Database.game_change_status(game['id'], 'played')
            Database.game_change_value(game['id'], 'end_ts', int(time.time()))
            game = Database.get_info(game['id'])
            MessagesSolo[game_id] = word_guessing(PlayerID, game)
            send_message(PlayerID, f"Вы проиграли. Вас зафачили. Вы отправляетесь на пересдачу. Вы не знаете такое слово - <b>{game['word']}</b>.")
            SoloGames.pop(game['id'])
            SoloPlay.pop(user_player['id'])
            GameSession.remove(PlayerID)
            return
        Database.game_change_value(game['id'], 'attemps', game['attemps'] - 2)
        game = Database.get_info(game['id'])
        MessagesSolo[game_id] = word_guessing(PlayerID, game)
        GameSession.remove(PlayerID)
        return
    Letter = m_message
    Letter = Letter.lower()
    Letter = Letter.replace('ё', 'е')
    if (Letter not in game['word']) and (game['attemps'] <= 1):
        for i in (MessagesSolo[game_id]):
            remove_message(PlayerID, i.message_id)
        Database.game_change_value(game['id'], 'attemps', 0)
        Database.game_change_status(game['id'], 'played')
        Database.game_change_value(game['id'], 'end_ts', int(time.time()))
        game = Database.get_info(game['id'])
        MessagesSolo[game_id] = word_guessing(PlayerID, game)
        SoloGames.pop(game['id'])
        SoloPlay.pop(user_player['id'])
        GameSession.remove(PlayerID)
        return send_message(PlayerID,
                           f"Вы проиграли. Вас зафачили. Вы отправляетесь на пересдачу - <b>{game['word']}</b>.")
    if (Letter not in game['word']):
        for i in (MessagesSolo[game_id]):
            remove_message(PlayerID, i.message_id)
        Database.game_change_value(game['id'], 'attemps', game['attemps'] - 1)
        game = Database.get_info(game['id'])
        MessagesSolo[game_id] = word_guessing(PlayerID, game)
        GameSession.remove(PlayerID)
        return
    if (Letter in game['word']):
        if Letter in SoloGames[game['id']]:
            remove_message(PlayerID, MessageID)
            GameSession.remove(PlayerID)
            return send_message(PlayerID, f"❌ Вы уже угадывали данную букву. Попробуйте повторить алфавит!")
        remove_message(PlayerID, MessageID)
        for i in (MessagesSolo[game_id]):
            remove_message(PlayerID, i.message_id)
        SoloGames[game['id']].append(Letter)
        MessagesSolo[game_id] = word_guessing(PlayerID, game)
        guessed_word = True
        for i in game['word']:
            if i not in SoloGames[game['id']]:
                guessed_word = False
        if guessed_word:
            SoloGames.pop(game['id'])
            SoloPlay.pop(user_player['id'])
            Database.game_change_status(game['id'], 'played')
            Database.game_change_value(game['id'], 'end_ts', int(time.time()))
            Database.PlayerIncreaseScore(user_player['id'], Database.get_info(game['id'])['attemps'] + 2)
            user_player = Database.PlayerGet(PlayerID)
            send_message(PlayerID, f"""
🥇 Ура! Вы угадали слово и пережили экзамен - <b>{game['word']}</b>.
Ваша жизнь спасена и вы получаете свой заслуженный отл 10. 
Теперь у вас <b>{user_player['score']}</b> очков.
""")
            GameSession.remove(PlayerID)
            return
        GameSession.remove(PlayerID)
        return
    GameSession.remove(PlayerID)
    return

def Fucker(PlayerID, Game):
    if (Game['attemps'] + 2 == 10) or (Game['attemps'] + 2 == 9) or (Game['attemps'] + 2 == 8):
        return 'халява'
    elif (Game['attemps'] + 2 == 7) or (Game['attemps'] + 2 == 6) or (Game['attemps'] + 2 == 5):
        return 'Полуфакер'
    elif (Game['attemps'] + 2 == 4) or (Game['attemps'] + 2 == 3):
        return 'Факер'
    else:
        return 'вас зафачил'

def word_guessing(PlayerID, Game):
    Player = Database.PlayerGet(PlayerID)
    word = ""
    for i in Game['word']:
        if i in SoloGames[Game['id']]:
            word = word + i + ' '
        else:
            word = word + '_ '
    text = ""
    message_id = send_message(PlayerID, f"""
<b>{word}</b>
{text}

Осталось попыток: {Game['attemps']}
""")
    send_message(PlayerID, f"""
                                🎁 На данный момент, ваша максимальная возможная оценка <b>{Mark(PlayerID, Game)}</b> <b>{Game['attemps'] + 2}</b> -. При ошибке,вы переходите к факеру Выше уровня и ваша оценка понижается на 1 балл .
                                """)

    sticker_id = send_sticker(PlayerID, Config.Stickers[Game['attemps']])
    send_message(PlayerID,
                f"Ваш экзаменатор <b>{Fucker(PlayerID, Game)}</b>")
    return (message_id, sticker_id)
    return (message_id,)
def Mark(PlayerID, Game):
    if (Game['attemps'] + 2 == 10) or (Game['attemps'] + 2 == 9) or (Game['attemps'] + 2 == 8):
        return 'отл'
    elif (Game['attemps'] + 2 == 7) or (Game['attemps'] + 2 == 6) or (Game['attemps'] + 2 == 5):
        return 'хор'
    elif (Game['attemps'] + 2 == 4) or (Game['attemps'] + 2 == 3):
        return 'уд'
    else: return 'неуд'

def Handler():
    @ExecutorBot.message_handler(content_types=["text"])
    def Analyzer(message):
        if (int(message.date) + 5) < int(time.time()):
            return
        player_id = message.chat.id
        user_message = message.text
        user_message_id = message.message_id
        if not (Database.player_existanse(player_id)):
            return welcome_on_server(player_id, user_message)
        user_player = Database.PlayerGet(player_id)
        if user_player['id'] in SoloPlay:
            return SoloMode(player_id, user_message, user_message_id)
        while (player_id in GameSession):
            time.sleep(0.2)
        commands = str(user_message).split(' ')
        input_command = commands[0].lower()
        if input_command == "профиль" or input_command == "/profile":
            user_player = Database.PlayerGet(player_id)
            return send_message(player_id, f"""
👨🏼‍💻 Профиль пользователя <b>{user_player['nick']}</b>

🆔️ Игровой ID: {user_player['id']}
🏆 Количество очков: {user_player['score']}
""")
        elif (input_command == "соло" or input_command == "/solo"):
            GameSession.append(player_id)
            generated_word = WordGenerator.get_word_from_list()
            StartTs = int(time.time())
            user_player = Database.PlayerGet(player_id)
            game_id = Database.GameSoloInit(
                user_player['id'],
                StartTs,
                generated_word
            )
            Game = Database.get_info(game_id)
            SoloPlay[user_player['id']] = game_id
            SoloGames[game_id] = list()
            print(f"""
S-Game #{Game['id']} | {user_player['nick']} | Word: {Game['word']}
""")
            send_message(player_id, f"""
            Вы можете ввести одну букву на русском языке, либо же назвать слово целиком, когда будете готовы.
            ℹ️ Внимание! Если вы не угадаете слово целиком, то вы потеряете 2 попытки.   
            """)
            MessagesSolo[game_id] = word_guessing(player_id, Game)
            GameSession.remove(player_id)
            return
        elif (input_command == "рейтинг" or input_command == "/rate"):
            Rating = Database.PlayerRating()
            rating_text = "📊 Рейтинг игроков: \n"
            place = 1
            for PlayerS in Rating:
                rating_text += '\n'
                rating_text += f"#{place} {'<b>' if (PlayerS['id'] == user_player['id']) else ''}{PlayerS['nick']} ({PlayerS['id']}){'</b>' if (PlayerS['id'] == user_player['id']) else ''} - {PlayerS['score']} очков."
                place += 1
            rating_text += '\n'
            rating_text += f"У вас - <b>{user_player['score']}</b> очков."
            rating_text += '\n\n'
            rating_text += 'Последние игры в <b>Соло</b> режиме:'
            LastGames = Database.GameLastSolo(user_player['id'])
            if len(LastGames) == 0:
                rating_text += '<pre>Нет последних сыгранных игр</pre>'
            else:
                for n in LastGames:
                    rating_text += '\n'
                    rating_text += f"Игра <b>{n['id']}</b> | Слово: <b>{n['word']}</b> | Результат: <b>{'Победа' if n['attemps'] > 0 else 'Проигрыш'}</b>"
            rating_text += '\n\n'
            send_message(player_id, rating_text)
        elif (input_command == "/rules") or (input_command == "правила"):
            return send_message(player_id, Config.Rules)
        else:
            send_message(player_id, """
👩🏻‍💻 <pre>Профиль</pre> - Ваш профиль игрока в боте. (/profile)

🧍‍️ <pre>Соло</pre> - Начать одиночную игру. (/solo)
За победу в одиночной игре вы можете получить <b>максиум 10 очков (тобиш отл 10)</b>.
n очков - слово угадано по буквам за n итераций не более 8. Положительная оценка уд3.
2 очка - слово угадано сразу.

🏆 <pre>Рейтинг</pre> - ТОП игроков и ваш рейтинг. (/rate)
Отображает пятёрку лучших игроков, а также последнюю историю ваших игр.

❗ <pre>Правила</pre> - Все правила игры. (/rules)
А также руководство для новичков.

""")


polling_thread = threading.Thread(target=bot_polling)
polling_thread.daemon = True
polling_thread.start()

if __name__ == "__main__":
    while True:
        try:
            time.sleep(120)
        except KeyboardInterrupt:
            break
