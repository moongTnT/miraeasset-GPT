import json
from functools import wraps

import pymysql

with open('conf.json') as f:
    config = json.load(f)


def with_db_connection(f):
    """
    함수 f의 시작 전 후에 DB 커넥션 연결과 종료를 해주는 데코레이터 입니다
    """
    @wraps(f)
    def with_db_connection_(*args, **kwargs):
        conn = pymysql.connect(**config["db_config"],
                               cursorclass=pymysql.cursors.DictCursor)
        try:
            ret = f(*args, connection=conn, **kwargs)
        except:
            conn.rollback()
            print("SQL failed")
            raise
        else:
            conn.commit()
        finally:
            conn.close()
        
        return ret
    
    return with_db_connection_

@with_db_connection
def fetch_data_from_db(*args, **kwargs):
    """
    query를 인자로 받아 실행하고 출력을 DataFrame으로 변경해주는 함수입니다
    """
    conn = kwargs.pop("connection")
    query = kwargs.pop("query")
    
    cursor = conn.cursor()
    
    cursor.execute(query)
    
    return cursor.fetchall()