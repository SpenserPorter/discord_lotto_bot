import sqlite3

class LottoryConnection(object):

    def __init__(self):
        self.sqlite_file = 'lottodb.sqlite'    # name of the sqlite database file

    def __enter__(self):
        self.connection = sqlite3.connect(self.sqlite_file)
        return self.connection

    def __exit__(self, type, value, traceback):
        self.connection.close()

def initialize_tables():
    table_data = {'user':{'user_id':'INTEGER PRIMARY KEY', 'balance':'REAL'},
                  'ticket':{'ticket_id':'INTEGER PRIMARY KEY', 'ticket_value':'TEXT', 'lottory_id':'INTEGER', 'user_id':'INTEGER'},
                  'lottory':{'lottory_id':'INTEGER PRIMARY KEY', 'jackpot':'INTEGER'},
                  }
    with LottoryConnection() as conn:
        curr = conn.cursor()
        for table_name, column_data in table_data.items():
            columns = []
            for column_name, column_type in column_data.items():
                columns.append('{cn} {ct}'.format(cn=column_name, ct=column_type))
            column_sql = '({})'.format(', '.join(columns))
            sql = 'CREATE TABLE IF NOT EXISTS {tn} {ts};'.format(tn= table_name, ts=column_sql)
            curr.execute(sql)
        conn.commit()

def add_lottory(jackpot=None):
    if jackpot is None:
        raise ValueError("Must provide a jackpot seed value to initialize a new lottory")

    with LottoryConnection() as conn:
        curr = conn.cursor()
        sql = 'INSERT INTO lottory (jackpot) VALUES ({jp});'.format(jp=jackpot)
        curr.execute(sql)
        conn.commit()

def get_lottory_jackpot(lottory_id):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        get_lottory = 'SELECT jackpot FROM lottory WHERE lottory_id = {id};'.format(id=lottory_id)
        curr.execute(get_lottory)
        lottory_id = curr.fetchone()
        return lottory_id

def add_user(user_id):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        add_user = 'INSERT OR IGNORE INTO user (user_id) VALUES ({id});'.format(id=user_id)
        curr.execute(add_user)
        conn.commit()

def add_ticket_to_user(ticket_value, lottory_id, user_id):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        add_ticket_sql = 'INSERT INTO ticket (ticket_value, lottory_id, user_id) VALUES ("{tv}", {ld}, {id});'.format(tv=ticket_value, ld=lottory_id, id=user_id)
        curr.execute(add_ticket_sql)
        conn.commit()

def get_current_lottory():
    with LottoryConnection() as conn:
        curr = conn.cursor()
        get_lotto_sql = 'SELECT * FROM lottory ORDER BY lottory_id DESC LIMIT 1;'
        curr.execute(get_lotto_sql)
        return curr.fetchone()[0]

def get_lottory_tickets(lottory_id):
        with LottoryConnection() as conn:
            curr = conn.cursor()
            get_tickets_sql = 'SELECT ticket_value, user_id FROM ticket WHERE lottory_id={};'.format(lottory_id)
            curr.execute(get_tickets_sql)
            return curr.fetchall()

def get_user_tickets(user_id, lottory_id=None):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        ld_sql = ' AND lottory_id = {ld}'.format(ld=lottory_id) if lottory_id is not None else ''
        get_ticket_sql = 'SELECT ticket_value FROM ticket WHERE user_id = {id}{ld};'.format(id=user_id, ld=ld_sql)
        curr.execute(get_ticket_sql)
        tickets = curr.fetchmany(100)
        output = []
        for ticket in tickets:
            output.append(ticket[0])
        return output
