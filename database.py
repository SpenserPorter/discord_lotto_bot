import sqlite3

class Connection(object):

    def __init__(self):
        self.sqlite_file = 'lottodb.sqlite'    # name of the sqlite database file

    def __enter__(self):
        self.connection = sqlite3.connect(self.sqlite_file)
        return self.connection

    def __exit__(self, type, value, traceback):
        self.connection.close()

def initialize_tables():
    table_data = {'user':{'user_id':'REAL PRIMARY KEY', 'balance':'REAL'},
                  'ticket':{'ticket_id':'INTEGER PRIMARY KEY', 'ticket_value':'TEXT', 'lottory_id':'INTEGER', 'user_id':'INTEGER'},
                  'lottory':{'lottory_id':'INTEGER PRIMARY KEY', 'jackpot':'INTEGER'},
                  }
    with Connection() as conn:
        with conn.cursor() as curr:
            for table_name, column_data in table_data.items():
                columns = []
                for column_name, column_type in column_data.items():
                    columns.append('{cn} {ct}'.format(cn=column_name, ct=column_type))
                column_sql = '({})'.format(', '.join(columns))
                sql = 'CREATE TABLE IF NOT EXISTS {tn} {ts};'.format(tn= table_name, ts=column_sql)
                print(sql)
                curr.execute(sql)
            conn.commit()

def add_lottory(jackpot=None):
    if jackpot is None:
        raise ValueError("Must provide a jackpot seed value to initialize a new lottory")

    with Connection() as conn:
        with conn.cursor() as cur:
            sql = 'INSERT INTO lottory (jackpot) VALUES {jp};'.format(jp=jackpot)
            curr.execute(sql)
            conn.commit()

def get_lottory_jackpot(lottory_id):
    with Connection() as conn:
        with conn.cursor() as curr:
            get_lottory = 'SELECT jackpot FROM lottory WHERE lottory_id = {id};'.format(id=lottory_id)
            curr.execute(get_lottory)
            lottory_id = curr.fetchone()
            return lottory_id

def add_user(user_id):
    with Connection() as conn:
        with conn.cursor() as curr:
            add_user = 'INSERT INTO user (user_id) VALUES {id} ON CONFLICT DO NOTHING;'.format(id=user_id)
            curr.execute(add_user)
            conn.commit()

def add_tickets_to_user(ticket_value, lottory_id, user_id):
    with Connection() as conn:
        with conn.cursor() as curr:
            add_ticket_sql = 'INSERT INTO ticket (ticket_value, lottory_id, user_id) VALUES ({tv} {ld} {id});'.format(tv=ticket_value, ld=lottory_id, id=user_id)
            curr.execute(add_ticket_sql)
            conn.commit()

def get_current_lottory():
    with Connection() as conn:
        with conn.cursor() as curr:
            get_lotto_sql = 'SELECT * FROM lottory ORDER BY lottory_id DESC LIMIT 1;'
            curr.execute(get_lott_sql)
            return curr.fetchone()

def get_user_tickets_ids(user_id, lottory_id=None):
    with Connection() as conn:
        with conn.cursor() as curr:
            ld_sql = 'AND lottory_id = {ld}'.format(ld=lottory_id) if lottory_id is not None else ''
            get_ticket_sql = 'SELECT ticket_id FROM ticket WHERE user_id = {id}{ld};'.format(id=user_id, ld=ld_sql)
            curr.execute(get_ticket_sql)
            return curr.fetchmany(100)

with Connection() as conn:
    initialize_tables()

add_lottory(50000)
add_user(42)
lottory_id = get_current_lottory()
add_ticket_to_user('5-3-8-1', lottory_id, 42)

print(get_user_tickets_ids(42, lottory_id))
