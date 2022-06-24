import psycopg2

# Функция, создающая структуру БД (таблицы)
def create_databases(cur):   
    cur.execute("""
        DROP TABLE IF EXISTS phones CASCADE;
        DROP TABLE IF EXISTS clients CASCADE;
    """)
    # conn.commit() #этот коммит нужен?

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(20) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR(40) UNIQUE DEFAULT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            phone_id SERIAL PRIMARY KEY,
            number VARCHAR(22) UNIQUE,
            client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE
        );
    """)
    conn.commit()

def new_data_insert(cur):
    cur.execute("""
        INSERT INTO clients(first_name, last_name, email)
        VALUES 
            ('Eli','Levy', 'levy@gmail.com'),
            ('Alex','Levy', 'a@gmail.com'),
            ('Katrin','Swan', 'swan@gmail.com'),
            ('Nolan','Robson', DEFAULT),
            ('Eli', 'Brown', DEFAULT);
    """)
    cur.execute("""
        INSERT INTO phones(number, client_id)
        VALUES
            ('(901)568-5464', '1'),
            ('972 52-7281828', '1'),
            ('972527241828', '2'),
            ('357 99 141340', '1');        
    """)
    conn.commit()

# Функция, позволяющая добавить нового клиента
def new_client_add(cur, _v):
    while _v:
        name = input("Input New Clients First Name ").capitalize()
        last = input("Input New Clients Last Name ").capitalize()
        email = input("Input e-mail, if not email input 'n'  ")
        if email.lower() == 'n' or email.find("@") == -1 or email.find(".") == -1:
            email = None
        cur.execute("""
            INSERT INTO clients(first_name, last_name, email)
            VALUES
                (%s, %s, %s) 
            RETURNING client_id;
            """, (name, last, email)
            )
        if input(f'Add client  {name} {last} Y/N?').lower() == 'y':
            conn.commit()
            print(f'Client {name} {last} added')
        add_phone(cur.fetchone()[0], True)
        if input('Input another client (Y/N)?  ').upper() == 'N':
            _v = False

# Функция, позволяющая добавить телефон для существующего клиента
def add_phone(id, _p):
    while _p:
        number_phone = input("Input phone number or push 'n' ")
        if number_phone.lower() != 'n':
            cur.execute("""
                INSERT INTO phones(number, client_id)
                VALUES (%s, %s);
                """, 
                (number_phone, id)
                )
            conn.commit()
            print(f'Phone number {number_phone} added')
        if input('Input another phone number (Y/N)?  ').lower() == 'n':
            _p = False
       
        
# Функция, позволяющая изменить данные о клиенте
def update_client(cur, id):
    update_data = input('Input data which update (name, lastname, email) ')
    new_data = input('Input new data ')
    if update_data.upper()[0] == 'N':
        cur.execute("""
            UPDATE clients SET first_name=%s 
            WHERE client_id=%s;
            """, (new_data.capitalize(), id)
        )
    elif  update_data.upper()[0] == 'L':
        cur.execute("""
            UPDATE clients SET last_name=%s 
            WHERE client_id=%s;
            """, (new_data.capitalize(), id)
        )
    elif update_data.upper()[0] == 'E':
        if new_data.find("@") == -1 or new_data.find(".") == -1:
            print("Email wrong")
            return 
        cur.execute("""
            UPDATE clients SET email=%s 
            WHERE client_id=%s;
            """, (new_data.lower(), id)
        )
    else:
        print("Request wrong")
    conn.commit()
    print('Data updated')

# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(cur, id):
    cur.execute("""
        SELECT number FROM phones
        WHERE client_id=%s;
        """, (id,)
    )
    print(cur.fetchall())
    del_phone = input("Input phone number for delete ")
    cur.execute("""
        DELETE FROM phones
        WHERE number=%s;
        """, (del_phone,)
    )
    if input(f'Delete phone number {del_phone} Y/N?').upper() == "Y":
        conn.commit()
        print(f'Phone number {del_phone} deleted')
    else:
        print('Deleting cancel')
# Функция, позволяющая удалить существующего клиента
def delete_client(cur, id):
    cur.execute("""
        SELECT * FROM clients
        WHERE client_id=%s;
        """, (id,)
        )
    clnt = cur.fetchone()
    cur.execute("""
        DELETE FROM clients 
        WHERE client_id=%s;
        """, (id,)
        )
    if input(f'Delete client {clnt[1]} {clnt[2]} Y/N? ').upper() == "Y":
        conn.commit()
        print(f'Client {clnt[1]} {clnt[2]} deleted')
    else:
        print('Deleting cancel')

# Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
def find_client(cur):
    name = input('Input first name ').capitalize()
    cur.execute("""
        SELECT client_id, first_name, last_name FROM clients 
        WHERE first_name=%s;
        """, (name,)
        )
    cl_id = _client_found(cur)
    if  cl_id is not None:
        return cl_id
    last = input('Input last name ').capitalize()
    cur.execute("""
        SELECT client_id, first_name, email FROM clients 
        WHERE (first_name=%s AND last_name=%s) OR (last_name=%s AND %s='');
        """, (name, last, last, name)
    )
    cl_id = _client_found(cur)
    if  cl_id is not None:
        return cl_id
    email = input('Choose email ').lower()
    cur.execute("""
        SELECT client_id, first_name, last_name FROM clients 
        WHERE (first_name=%s AND last_name=%s AND email=%s) OR (%s='' AND last_name=%s AND email=%s) OR (first_name=%s AND %s='' AND email=%s) OR (%s='' AND %s='' AND email=%s);
        """, (name, last, email, name, last, email, name, last, email, name, last, email)
    )
    cl_id = _client_found(cur)
    if  cl_id is not None:
        return cl_id
    phone = input('Input phone number ')
    cur.execute("""
        SELECT client_id, phone_id, number FROM phones 
        WHERE number=%s;
        """, (phone,)
    )
    cl_id = _client_found(cur)
    if  cl_id is not None:
        return cl_id

def _client_found(cur):
    clnt = cur.fetchall()
    # print(clnt)
    if len(clnt) == 1:
        print(f"Client '{clnt[0][1]} {clnt[0][2]}' found")
        return clnt[0][0]
    elif clnt == []:
        print('Client not found')
    else:
        print([cl[2] for cl in clnt])


# КОНЕЦ функций

if __name__  == '__main__':
    with psycopg2.connect(database='contact_db', user='postgres', password='Bb19690226') as conn:
        with conn.cursor() as cur:
# Открыть базу и заполнить новыми данными
            create_databases(cur)
            new_data_insert(cur)
            _ = True
            while _:
                v = input(f"""Input   'a' for add new client,
        'p' for add new phone,
        'u' for update client\'s dates,
        'dp' for delete client\'s phone,
        'd  for delete existing client,
        'f' for find existing clients,
        'q' for quit
            """).lower()
                if v == 'a':
# Добавить нового клиента
                    print('Add new client')
                    new_client_add(cur, True)
                elif v == 'p':
#  Добавление нового телефона
                    print('Add new phone existing client')
                    id = find_client(cur)
                    add_phone(id, True)
                elif v == 'u':
# Изменить данные о клиенте
                    print('Update existing client')
                    id = find_client(cur)
                    if id is not None:
                        update_client(cur, id)
                    else:
                        print('Client not found')
                elif v == 'dp':
# Удалить телефон для существующего клиента
                    print('Delete phone number of existing client')
                    id = find_client(cur)
                    if id is not None:
                        delete_phone(cur, id)
                    else:
                        print('Client not found')
                elif v == 'd':
# Удалить существующего клиента
                    print('Delete existing client')
                    id = find_client(cur)
                    if id is not None:
                        delete_client(cur, id)
                    else:
                        print('Client not found')
                elif v == 'f':
# Найти клиента по его данным (имени, фамилии, email-у или телефону)
                    print('Find client')
                    id = find_client(cur)
                elif v == 'q':
                    _ = False
                else:
                    print('Introduce incorrect command')
# Наблюдаем за таблицами
            cur.execute("""
                SELECT * FROM clients ;
            """)
            print(cur.fetchall())
            cur.execute("""
                SELECT * FROM phones;
            """)
            print(cur.fetchall())  # запрос данных автоматически зафиксирует изменения