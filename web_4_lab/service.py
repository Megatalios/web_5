from sqlalchemy import text
from flask import session, make_response, redirect, url_for, jsonify
import bcrypt

from web_4_lab.utils import get_db


def get_all_clients():
    return get_db().session.execute(text("SELECT * FROM clients")).mappings().all()


# Получаем запрос с фильтром по id
def get_client(id_: int):
    return get_db().session.execute(text(f"SELECT * FROM clients WHERE id = {id_}")).mappings().all()


# # Получаем все запросы по имени автора
def get_client_by_name(name: str):
    result = []
    rows = get_db().session.execute(text(f"SELECT * FROM clients WHERE name = '{name}'")).mappings().all()
    for row in rows:
        result.append(dict(row))
    return {'clients': result}


def create_client(name: str, mail: str, phone_number: str, message: str):
    get_db().session.execute(text(
        f"INSERT INTO clients "
        f"(name, mail, phone_number, message) "
        f"VALUES ("
        f"'{name}', "
        f"'{mail}', "
        f"'{phone_number}', "
        f"'{message}'"
        f")"
    ))
    get_db().session.commit()
    client_id = get_db().session.execute(text("SELECT last_insert_rowid()")).scalar()
    return dict(get_client(id_=client_id))


def remove_client_by_id(id_: int):
    get_db().session.execute(text(f"DELETE FROM clients WHERE id = {id_}"))
    get_db().session.commit()


def login_user(form_data):
    username = form_data.get('name')
    password = form_data.get('password')
    if username == '':
        return redirect(url_for('/login'))
    # Ищем пользователя в БД
    result = get_db().session.execute(text(f"SELECT * FROM logins WHERE name = '{username}'")).mappings().one_or_none()
    # если пользователь не найден переадресуем на страницу /login
    if result is None:
        print("result is None")
        return redirect(url_for('login'))
        
    # for row in result:
    #     row_dict = dict(row._mapping.items())
    #     result.append(row_dict)
    # user = dict(result)
    user = {'result': result}
    # если пароль не прошел проверку, переадресуем на страницу /login
    if 'password' in user and not bcrypt.checkpw(password.encode('utf-8'), user.get('password').encode('utf-8')):
        print("Пароль не прошел проверку")
        return redirect(url_for('login'))
    # иначе регистрируем сессию пользователя (записываем логин пользователя в параметр user)
    # и высылаем cookie "AuthToken"
    else:
        # print("Пароль подошел, но что-то идет не так")
        response = redirect('/')
        print(user['result'].keys())
        session['user'] = user['result']['name']
        session['userId'] = user['result']['id']
        response.set_cookie('AccountToken', user['result']['name'])
        return response
    

# Создание пользовательского аккаунта
def register_user(form_data):
    # Получаем данные пользователя из формы
    username = form_data.get('name')
    password = form_data.get('password')
    email = form_data.get('email')
    # Проверяем полученные данные на наличие обязательных полей
    if username == '' or password == '' or email == '':
        return make_response(jsonify({'message': 'The data entered are not correct!'}), 400)
    # Создаем хеш пароля с солью
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    try:
        get_db().session.execute(text(f"INSERT INTO logins "
                           f"(name, password, mail) "
                           f"VALUES ("
                           f"'{username}', "
                           f"'{hashed}', "
                           f"'{email}'"
                           ")"))
        # Подтверждение изменений в БД
        get_db().session.commit()
        # Переадресуем на страницу авторизации
        return redirect(url_for('login'))
        # если возникла ошибка запроса в БД
    except Exception as e:
        # откатываем изменения в БД
        get_db().session.rollback()
        # возвращаем response с ошибкой сервера
        return make_response(jsonify({'message': str(e)}), 500)