import random
# Можно изменить токе на свой
token = "6677512022:AAFDHryAkNBr6-mIQ0h7t8NQ1CxBaUvgGSs"
interval_to_response = 3
timeout = 3
db_path = 'project_storage/user_data.sql'
dic_path = 'project_storage/mipt_slang_dic.txt'

HelloWorld = {
"""
Добро пожаловать, на сервер МФТИ. Место, где каждый хочет тебя зафачить, а твоя главная задача выжить.
Отправь свой ник, чтобы продолжить!

<i>Введите ник, состоящий из Ascii-символов  длиной от 4 до 14.
Использовать специальные символы запрещено.
Во избежания читерства и обмана факеров, смена никнейма не предусмотренна. У вас есть один шанс пережить Физтех</i>
    """
}
ReRead = {
"""
Данный физтех уже находится в игре. Выбери уникальное имя
<i>Рекомендуемое значение: U > 10 Voltage</i>
"""
}
Stickers = {
    0: 'CAACAgIAAxkBAAEK02FlY_1CuH3Kh8TJpdYdvRLMfK8LMQADIwACEaJQSRUciyd__34ZMwQ',
    1: 'CAACAgIAAxkBAAEK019lY_xkYv-CWSAgohC0oT_XmVbHHgACGQADCkioAAGDltfaVdsyNzME',
    2: 'CAACAgIAAxkBAAEK011lY_po4PZFkrMTp34Upbdp3aXMiAACqgwAAkO_0Um4Lz1V1Ar2BjME',
    3: 'CAACAgIAAxkBAAEK01FlY_jNtr5tMkuUpujMiXoMlqBQTQACzx8AAqSmOUopt0Tt_nIW3zME',
    4: 'CAACAgIAAxkBAAEK01dlY_lNj67X-aNWgJ_vfIF7hizFKgAC-zoAAvTOyEuh49U-6dXGIjME',
    5: 'CAACAgIAAxkBAAEK01tlY_pBvlF9RycSmyCu1b374npzggACLAAD2JsMFFmlEqDIRKeLMwQ',
    6: 'CAACAgIAAxkBAAEK01VlY_kbx4JO2w5wTbip5JS0d2FmVQACIwADCkioAAGRhaQJQInhyTME',
    7: 'CAACAgIAAxkBAAEK01llY_mYX7iYk8fsFB-8wY9mJbm_XQACRSAAAkb7OErVwrqxsQwT0DME',
    8: 'CAACAgIAAxkBAAEK00xlY-7A8XaBlH-OGrx9CHIKxNVvggACAScAApabMEoaMifAARkEyTME'
}
Rules = """
📌 Отгадай сленг тру физтеха.
<b>Одиночная игра</b> - cражайся против факеров физтеха в одиночку.
<b>Игра против противника/противников</b> - TO-DO.

1. Одиночная игра даёт возможность получить <b>1 очко</b>, если слово угадывалось побуквенно и <b>2 очка</b>, 
если слово было угаданно полностью и написано в чат как ответ.
2. TO-DO
3. Буквы "ё" и "е" равносильны. Также, не играет роли и регистр отправляемых букв и слов.
5. За  попытку накрутки очков, обхода систем вы отправляетесь на пересдачу, а так же будете писать обисос.
"""

class WordGen():
    def __init__(self, dict_dir):
        self.lines = open(dict_dir, encoding="utf-8").read().splitlines()
    def get_word_from_list(self):
        word = random.choice(self.lines)
        while len(word) > 7:
            word = random.choice(self.lines)
        return word