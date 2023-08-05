import fastapi
from fastapi import FastAPI

import pydantic_models
from database import crud

api = FastAPI()


# ------------------- Users --------------------- #
@api.post('/user/create')
def create_user(user: pydantic_models.UserToCreate):
    """Создание пользователя"""
    return crud.create_user(tg_id=user.tg_ID,
                            nick=user.nick if user.nick else None).to_dict()


@api.put('/user/{user_id}')
def update_user(user_id: int, user: pydantic_models.UserToUpdate = fastapi.Body()):
    """Обновление пользователя"""
    if user_id == user.id:
        return crud.update_user(user).to_dict()


@api.delete('/user/{user_id}')
@crud.db_session
def delete_user(user_id: int = fastapi.Path()):
    """Удаление пользователя"""
    crud.get_user_by_id(user_id).delete()
    return True


@api.get('/get_info_by_user_id/{user_id:int}')
@crud.db_session
def get_info_about_user(user_id: int):
    """Получение информации о пользователе"""
    return crud.get_user_info(crud.User[user_id])


@api.get('/get_user_balance_by_id/{user_id:int}')
@crud.db_session
def get_user_balance_by_id(user_id: int):
    """Получение баланса пользователя"""
    crud.update_wallet_balance(crud.User[user_id].wallet)
    return crud.User[user_id].wallet.balance


@api.get("/users")
@crud.db_session
def get_users():
    """Получение списка пользователей"""
    users = []
    for user in crud.User.select()[:]:
        users.append(user.to_dict())
    return users


@api.get("/user_by_tg_id/{tg_id:int}")
@crud.db_session
def get_user_by_tg_id(tg_id: int):
    """Получение пользователя по id телеграма"""
    user = crud.get_user_info(crud.User.get(tg_ID=tg_id))
    return user


@api.get("/get_user_wallet/{user_id:int}")
@crud.db_session
def get_user_wallet(user_id):
    return crud.get_wallet_info(crud.User[user_id].wallet)


@api.get("/get_user_transactions/{user_id:int}")
@crud.db_session
def get_user_wallet(user_id):
    return crud.get_user_transactions(user_id)


# ------------------- Users --------------------- #

# ------------------- Transactions --------------------- #

@api.post("/create_transaction/{user_id:int}")
@crud.db_session
def create_transaction(
        receiver_address: str = fastapi.Body(),
        amount_btc_without_fee: float = fastapi.Body(),
        user_id: int = fastapi.Path()):
    """
    Создание транзакции
    :param receiver_address: адрес кошелька получателя
    :param amount_btc_without_fee: количество биткоинов исключая комиссию, значение в сатоши
    :param user_id: id отправителя
    :return: User
    """
    user = crud.get_user_by_id(user_id)
    transaction = crud.create_transaction(user, amount_btc_without_fee, receiver_address, testnet=True)
    crud.update_all_wallets()
    return crud.get_transaction_info(transaction)


@api.get("/transactions")
@crud.db_session
def get_transactions():
    """Получение всех транзакций"""
    transactions = []
    for transaction in crud.Transaction.select()[:]:
        transactions.append(transaction.to_dict())
    return transactions


# ------------------- Transactions --------------------- #


@api.get('/get_total_balance')
@crud.db_session
def get_total_balance():
    """Получение общего баланса"""
    balance = 0.0
    crud.update_all_wallets()
    for user in crud.User.select()[:]:
        balance += user.wallet.balance
    return balance


@api.get("/wallets")
@crud.db_session
def get_wallets():
    """Получение всех кошельков"""
    wallets = []
    for wallet in crud.Wallet.select()[:]:
        wallets.append(wallet.to_dict())
    return wallets
