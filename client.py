import requests
import pydantic_models
from config import api_url


def update_user(user: dict):
    """Обновляем пользователя"""
    # валидируем данные о юзере, так как мы не под декоратором fastapi и это нужно делать вручную
    user = pydantic_models.UserToUpdate.model_validate(user)
    # чтобы отправить пост запрос - используем метод .post, в аргументе data - отправляем строку в формате json
    responce = requests.put(f'{api_url}/user/{user.id}', data=user.model_dump_json())
    try:
        return responce.json()
    except:
        return responce.text


def delete_user(user_id: int):
    """
    Удаляем пользователя
    :param user_id:
    :return:
    """
    return requests.delete(f'{api_url}/user/{user_id}').json()


def create_user(user: pydantic_models.UserToCreate):
    """
    Создаем пользователя
    :param user:
    :return:
    """
    user = pydantic_models.UserToCreate.model_validate(user)
    return requests.post(f'{api_url}/user/create', data=user.model_dump_json()).json()


def get_info_about_user(user_id):
    """
    Получаем инфу по пользователю
    :param user_id:
    :return:
    """
    return requests.get(f'{api_url}/get_info_by_user_id/{user_id}').json()


def get_user_balance_by_id(user_id):
    """
    Получаем баланс пользователя
    :param user_id:
    :return:
    """
    responce = requests.get(f'{api_url}/get_user_balance_by_id/{user_id}')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_total_balance():
    """
    Получаем общий баланс

    :return:
    """
    responce = requests.get(f'{api_url}/get_total_balance')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_users():
    """
    Получаем всех пользователей
    :return list:
    """
    return requests.get(f"{api_url}/users").json()


def get_user_wallet_by_tg_id(tg_id):
    user_dict = get_user_by_tg_id(tg_id)
    return requests.get(f"{api_url}/get_user_wallet/{user_dict['id']}").json()


def get_user_by_tg_id(tg_id):
    """
    Получаем пользователя по айди его ТГ
    :param tg_id:
    :return:
    """
    return requests.get(f"{api_url}/user_by_tg_id/{tg_id}").json()


def get_user_transactions(user_id: int):
    """
    Получаем все транзации пользователя
    :param user_id:
    :return:
    """
    responce = requests.get(f"{api_url}/get_user_transactions/{user_id}")
    try:
        return responce.json()
    except Exception as E:
        return f"{responce.text} \n" \
               f"Exception: {E.args, E.__traceback__}"


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    user_dict = get_user_by_tg_id(tg_id)
    payload = {'receiver_address': receiver_address,
               'amount_btc_without_fee': amount_btc_without_fee}
    responce = requests.post(f"{api_url}/create_transaction/{user_dict['id']}", json=payload)
    return responce.text
