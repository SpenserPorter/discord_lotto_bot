import sqlite3

class LottoryConnection(object):

    def __init__(self):
        self.sqlite_file = 'data/lottodb.sqlite'    # name of the sqlite database file

    def __enter__(self):
        self.connection = sqlite3.connect(self.sqlite_file, timeout=30.0)
        return self.connection

    def __exit__(self, type, value, traceback):
        self.connection.close()

def initialize_tables():
    table_data = {'user':{'user_id':'INTEGER PRIMARY KEY', 'balance':'REAL DEFAULT 0', 'income': 'INTEGER DEFAULT 0', 'outflow': 'INTEGER DEFAULT O'},
                  'ticket':{'ticket_id':'INTEGER PRIMARY KEY', 'ticket_value':'TEXT', 'lottory_id':'INTEGER', 'user_id':'INTEGER'},
                  'lottory':{'lottory_id':'INTEGER PRIMARY KEY', 'jackpot':'INTEGER DEFAULT 0', 'income': 'INTEGER DEFAULT 0', 'outflow': 'INTEGER DEFAULT 0'},
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

def add_lottory(jackpot=0):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        sql = 'INSERT INTO lottory (jackpot) VALUES ({jp});'.format(jp=jackpot)
        curr.execute(sql)
        conn.commit()

def get_lottory_jackpot_prog(lottory_id):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        get_lottory = 'SELECT jackpot FROM lottory WHERE lottory_id = {id};'.format(id=lottory_id)
        curr.execute(get_lottory)
        lottory_jackpot = curr.fetchone()
        return lottory_jackpot[0]

def modify_lottory_jackpot_prog(lottory_id, amount):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        get_balance_sql = 'SELECT jackpot FROM lottory WHERE lottory_id = {};'.format(lottory_id)
        curr.execute(get_balance_sql)
        current_balance = curr.fetchone()[0]
        new_balance = current_balance + amount
        set_balance_sql = 'REPLACE INTO lottory (lottory_id, jackpot) VALUES ({},{});'.format(lottory_id, new_balance)
        curr.execute(set_balance_sql)
        conn.commit()
        return new_balance

def update_lottory_stats(lottory_id, income, outflow):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        sql = 'REPLACE INTO lottory (lottory_id, income, outflow) VALUES ({ld},{ic},{of});'.format(ld=lottory_id, ic=income, of=outflow)
        curr.execute(sql)
        conn.commit()

def get_lottory_stats(lottory_id=None):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        lottory_id_sql = '' if lottory_id is None else ' WHERE lottory_id={}'.format(lottory_id)
        sql = 'SELECT income, outflow FROM lottory{};'.format(lottory_id_sql)
        curr.execute(sql)
        return curr.fetchall()


def add_user(user_id):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        add_user = 'INSERT OR IGNORE INTO user (user_id) VALUES ({id});'.format(id=user_id)
        curr.execute(add_user)
        conn.commit()

def get_user(user_id=None):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        one_user = '' if user_id is None else 'WHERE user_id={}'.format(user_id)
        get_user_sql = 'SELECT user_id FROM user{};'.format(one_user)
        curr.execute(get_user_sql)
        return curr.fetchall()


def add_ticket_to_user(ticket_list, lottory_id, user_id):
    with LottoryConnection() as conn:
        batch_size = 100000
        curr=conn.cursor()
        curr.execute("PRAGMA synchronous = OFF")
        curr.execute("PRAGMA journal_mode = MEMORY")
        curr.execute('BEGIN TRANSACTION')
        add_ticket_sql = 'INSERT INTO ticket (ticket_value, lottory_id, user_id) VALUES (?,?,?)'
        for n in range(0, len(ticket_list), batch_size):
            values_list = map(lambda x: (str(x), lottory_id, user_id), ticket_list[n:n+batch_size])
            curr.executemany(add_ticket_sql, values_list)
            conn.commit()

def get_user_balance(user_id):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        get_balance_sql = 'SELECT balance FROM user WHERE user_id = {};'.format(user_id)
        curr.execute(get_balance_sql)
        return curr.fetchone()[0]

def modify_user_balance(user_id, amount):
    with LottoryConnection() as conn:
        curr = conn.cursor()
        get_balance_sql = 'SELECT balance FROM user WHERE user_id = {};'.format(user_id)
        curr.execute(get_balance_sql)
        current_balance = curr.fetchone()[0]
        new_balance = current_balance + amount
        set_balance_sql = 'REPLACE INTO user (user_id, balance) VALUES ({},{});'.format(user_id, new_balance)
        curr.execute(set_balance_sql)
        conn.commit()
        return new_balance

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
        tickets = curr.fetchall()
        output = []
        for ticket in tickets:
            output.append(ticket[0])
        return output
