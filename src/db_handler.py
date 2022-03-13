import os
import sys
import psycopg2
from datetime import datetime, timezone, timedelta
from psycopg2.extras import DictCursor


class DBHandler:
    def __init__(self):
        self.database_url = os.environ["DATABASE_URL"]

    def exec_query(self, query_str):
        try:
            with psycopg2.connect(self.database_url, sslmode='require') as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query_str)
        except Exception as e:
            print(e.__str__())

    def get_last_update_of_drestaurant_list(self):
        """
        drestaurant_listの前回の更新日時を返す。
        """
        table_name = "drestaurant_list"
        query_str = f"SELECT * FROM {table_name} limit 1"
        try:
            with psycopg2.connect(self.database_url, sslmode='require') as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query_str)
                    result = cur.fetchone()
        except Exception as e:
            print(e.__str__())
            sys.exit()
        return result["last_update"]

    def insert_record_to_drestaurant_list(self, restaurant_name, type_str):
        """
        レストラン一覧に情報を追加する。
        """
        dt_now = str(datetime.now(timezone(timedelta(hours=9))))
        query_str = f"insert into drestaurant_list (restaurant_name,type,last_update) values (\'{restaurant_name}\',\'{type_str}\',\'{dt_now}\')"
        print("insert")
        self.exec_query(query_str)

    def delete_all_record(self, table_name):
        """
        対象テーブルのレコードをすべて削除する。
        """
        query_str = f"delete from {table_name}"
        self.exec_query(query_str)

    def update_drestaurant_status(self, target_date: datetime, restaurant_name: str, status: bool):
        table_name = "drestaurant_status"
        dt_now = str(datetime.now(timezone(timedelta(hours=9))))
        query_str = f"INSERT INTO {table_name} (target_date,restaurant_name,available,last_update) values (\'{target_date.strftime('%Y-%m-%d')}\',\'{restaurant_name}\',\'{status}\',\'{dt_now}\')" \
                    f"ON conflict (target_date,restaurant_name)" \
                    f"DO UPDATE SET available=\'{status}\',last_update=\'{dt_now}\'"
        self.exec_query(query_str)

    def delete_drestaurant_status(self, target_date: datetime, restaurant_name):
        table_name = "drestaurant_status"
        datetime_str = target_date.strftime('%Y-%m-%d')
        query_str = f"DELETE FROM {table_name} WHERE target_date = \'{datetime_str}\' and restaurant_name = \'{restaurant_name}\'"
        self.exec_query(query_str)

    def select_from_drestaurant_status_dict(self, target_date: datetime):
        table_name = "drestaurant_status"
        query_str = f"SELECT * FROM {table_name} where target_date = \'{target_date.strftime('%Y-%m-%d')}\'"
        result_dict = {}
        try:
            with psycopg2.connect(self.database_url, sslmode='require') as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query_str)
                    for row in cur:
                        result_dict[row["restaurant_name"]] = row["available"]
        except Exception as e:
            print(e.__str__())
            sys.exit()
        return result_dict

    def delete_unnecessary_records(self):
        dt_now = datetime.now(timezone(timedelta(hours=9)))
        table_name = "drestaurant_status"
        query_str = "DELETE FROM " + table_name + " where target_date < " + "\'" + dt_now.strftime('%Y-%m-%d') + "\'"
        self.exec_query(query_str)

