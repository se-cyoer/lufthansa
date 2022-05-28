import time
import pandas as pd
from lufthansa.lufthansa.db.redisdb import RedisDB
import json
import os

class Settings:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def read_file(self):
        df = pd.read_csv(self.file_name)
        return df, len(df)

    def read_ticket_info(self):
        df = self.read_file()[0]
        ticket_info = df.loc[:, 'ticket_date':'ticket_target']
        ticket_date = ticket_info.iloc[:, 0].values
        ticket_resource = ticket_info.iloc[:, 1].values
        ticket_target = ticket_info.iloc[:, 2].values
        return {'field': {
            'ticket_date': ticket_date,
            'ticket_resource': ticket_resource,
            'ticket_target': ticket_target
        }, 'count': self.read_file()[1]}

    def read_user_info(self):
        df = self.read_file()[0]
        user_info = df.iloc[:, 3:]
        first_name = user_info.iloc[:, 0].values
        last_name = user_info.iloc[:, 1].values
        phone = user_info.iloc[:, 2].values
        email = user_info.iloc[:, 3].values
        gender = user_info.iloc[:, 4].values
        return {'field': {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,
            'gender': gender
        }, 'count': self.read_file()[1]}

    def count_(self):
        count = self.read_file()[1]
        return count

    def create_task_name(self):
        task_names = list()
        counts = self.count_()
        ticket = self.read_ticket_info()
        user = self.read_user_info()
        for count in range(counts):
            task_name = f"{ticket.get('field').get('ticket_date')[count]}_" \
                        f"{ticket.get('field').get('ticket_resource')[count]}_" \
                        f"{ticket.get('field').get('ticket_target')[count]}_" \
                        f"{user.get('field').get('phone')[count]}"
            task_names.append(task_name)
        return task_names

    # def create_task_file(self):
    #     # redisdb = RedisDB(ip_ports="localhost:6379", db=0)
    #     file_names = self.create_task_name()
    #     for file_name in file_names:
    #         # datas = redisdb.zget('b', count=-1, is_pop=False)
    #         with open(f'{file_name}.json', 'w') as fp:
    #             json.dump({'a': 'a'}, fp)
    #             fp.close()
    #
    # def task_table(self):
    #     table_name = self.create_task_table_name()
    #     with open('task_table_name/task_table_file.txt', 'a') as fp:
    #         fp.write(table_name)
    #         fp.close()
    #     return table_name
    #
    # def delete_task_table(self):
    #     file = "task_table_name/task_table_file.txt"
    #     now_t = time.time()
    #     datas = list()
    #     with open(file, 'r') as fp:
    #         lines = fp.readlines()
    #         for line in lines:
    #             t = float(line.split('_')[-1]) + 600
    #             if now_t > t:
    #                 return True
    #             else:
    #                 datas.append(line)
    #                 return False
    #     os.remove(file)
