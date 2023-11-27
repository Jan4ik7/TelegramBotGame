import sqlite3 as SQLdriver
import threading

class Database():
    def __init__(self, db_name : str):
        self.Connection = SQLdriver.connect(
            db_name,
            check_same_thread = False,
            isolation_level = None
        )
        self.Cursor = self.Connection.cursor()
        self.locker = threading.Lock()
    def execute(self, request, type : str = 'none'):
        self.locker.acquire()
        resultset = None
        try:
            if type == 'none':
                self.Cursor.execute(request)
                self.Connection.commit()
            elif type == 'one':
                self.Cursor.execute(request)
                resultset = self.Cursor.fetchone()
            elif type == 'many':
                self.Cursor.execute(request)
                resultset = self.Cursor.fetchall()
        except Exception as e:
            print(f"#database | Exception on cursor: {e}.")
        finally:
            self.locker.release()
        return resultset
    def GetAll(self):
        info = self.execute("SELECT * FROM `users`", 'many')
        full_list = list()
        for Player in info:
            full_list.append(self.PlayerGetById(Player[0]))
        return full_list
    def player_existanse(self, tg_id):
        isExist = self.execute(f"SELECT `id` FROM `users` WHERE `tg_id` = {tg_id}", 'one')
        return not (isExist == None)
    def PlayerNickIsUsed(self, nick):
        isExist = self.execute(f"SELECT `id` FROM `users` WHERE `nick` = '{nick}'", 'one')
        return not (isExist == None)
    def PlayerCreate(self, tg_id, nick):
        return self.execute(f"INSERT INTO `users` (`tg_id`, `nick`) VALUES ({tg_id}, '{nick}')")
    def PlayerGet(self, tg_id):
        Data = self.execute(f"SELECT * FROM `users` WHERE `tg_id` = {tg_id}", 'one')
        return {
            'id': int(Data[0]),
            'tg_id': int(Data[1]),
            'nick': str(Data[2]),
            'level': int(Data[3]),
            'score': int(Data[4]),
        }
    def PlayerGetById(self, id):
        Data = self.execute(f"SELECT * FROM `users` WHERE `id` = {id}", 'one')
        return {
            'id': int(Data[0]),
            'tg_id': int(Data[1]),
            'nick': str(Data[2]),
            'level': int(Data[3]),
            'score': int(Data[4]),
        }
    def PlayerRating(self):
        Data = self.execute("SELECT * FROM `users` ORDER BY `score` DESC LIMIT 5", 'many')
        ret_list = list()
        for Player in Data:
            try:
                ret_list.append(self.PlayerGetById(Player[0]))
            except:
                None
        return ret_list
    def PlayerIncreaseScore(self, id, incnum):
        return self.execute(f"UPDATE `users` SET `score` = `score` + {incnum} WHERE `id` = {id}")
    def GameSoloInit(self, player_id, start_ts, word):
        self.execute(f"INSERT INTO `games` (`tg_id`, `start_ts`, `word`) VALUES ({player_id}, {start_ts}, '{word}')")
        return self.Cursor.lastrowid
    def GameLastSolo(self, id):
        Data = self.execute(f"SELECT * FROM `games` WHERE (`tg_id` = {id}) ORDER BY `id` DESC LIMIT 5", 'many')
        RetList = list()
        for G in Data:
            RetList.append(self.get_info(G[0]))
        return RetList
    def get_info(self, game_id):
        Data = self.execute(f"SELECT * FROM `games` WHERE `id` = {game_id}", 'one')
        return {
            'id': int(Data[0]),
            'tg_id': int(Data[1]),
            'start_ts': int(Data[2]),
            'end_ts': int(Data[3]),
            'status': str(Data[4]),
            'word': str(Data[5]),
            'attemps': int(Data[6]),
        }
    def game_change_value(self, id, var, val):
        return self.execute(f"UPDATE `games` SET `{var}` = {val} WHERE `id` = {id}")
    def game_change_status(self, id, status):
        return self.execute(f"UPDATE `games` SET `status` = '{status}'")