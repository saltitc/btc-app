# FastAPI bitcoin app

This project was written using fastapi, pyTelegramBotAPI and the bit library for working with bitcoin. When you first launch a telegram bot, a crypto wallet is created for you, you can check your balance, send bitcoin to other wallets and view your transaction history. An admin panel has been added for the administrator, where he can view all users, information about them, delete a specific user, view the total balance of all users

## Structure
```
├── database                             # Database files
│   ├── crud.py                          # A set of functions that allows to work with the database
│   ├── db.py                            # For binding to the database and matching entities with database tables
│   └── models.py                       
├── tg_bot.py                            # Telegram bot code that sends requests to api from the client
├── client.py                            # HTTP client to work with api
├── app.py                               # Handling API requests
├── config.py                            # Configuration file
├── pydantic_models.py                   # To validate the data that the server receives and sends
├── requirements.txt                     # All libraries used in the project
├── .gitignore                           # Files that git shouldn't track
└── README.md
```

## Approximate principle of operation
<img width="1056" alt="image" src="https://github.com/saltitc/btc-app/assets/114296895/d7118a8a-b3f8-46c7-87b6-9ed2669ea41c">

[Click to see the diagram for yourself](https://whimsical.com/user-4aXiPBnfWnLm7W4jfk8Hon)
___
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them


+ [Python](https://www.python.org/downloads/)
+ [PyCharm IDE](https://www.jetbrains.com/ru-ru/pycharm/download/?section=windows)
+ [Postman](https://www.postman.com) (if you want to test api)


### Installing

A step by step series of examples that tell you how to get a development env running

+ Create a folder for the repository and create a virtual environment in it. To do this, launch a terminal and enter the following commands
```
mkdir btc-app
cd btc-app
python3 -m venv venv
```
+ Open this project in Pycharm IDE and enter the following commands in the built in terminal to clone the repository and install the packages
```
git clone https://github.com/saltitc/btc-app.git
pip install --upgrade pip
pip install -r btc-app/requirements.txt
```
+ To create a database and bind all entities to it, write the following command in the terminal
```
python3 btc-app/database/db.py
```
> If this command produces an error `ModuleNotFoundError: No module named 'database'`, replace the import line `from database.models import *` with `from models import *` in database/db.py
+ Create a config.py file and create variables
```
bot_token = 'token'  # Receipt instructions are below.
tg_admin_id = 'your_telegram_id'  # How to get it will be indicated below, but for now, specify None

api_url = "http://127.0.0.1:8000"
username = "admin"
password = "$2b$12$fqf.wnDdBYGq7CWQAvk4m.KnMYzmTan77O5MI99H/sBtzz3625xrG"  # Receipt instructions are below.
ALGORITHM = "HS256"
SECRET_KEY = "fd6c326...dcc3d00ceada42...572c648e26...1fcf9a9af"  # Receipt instructions are below.
```
> To get a bot token, you need to:
>> 1. Find and run @BotFather in telegram
>> 2. Write `/start` and `/newbot` commands
>> 3. Submit bot name and username
>> 4. In response, the BotFather will send you your bot token in the form `11111111111:AAAAAAAAaaaAAAA`

> To get the password hash:
>> 1. Run config.py in python console <img width="879" alt="Снимок экрана 2023-08-12 в 16 37 24" src="https://github.com/saltitc/btc-app/assets/114296895/7786e3d1-48e0-45c0-99a3-757777bd40f5">
>> 2. Write this code
>>> ```python
>>> from passlib.context import CryptContext
>>> pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
>>> pwd_context.hash('your_password')
>>> ```
>> 3. In response, you will receive a hash of your password, which you must assign to the password variable
>> 4. You need to pass the unhashed password to the password parameter on line 7 of the client.py file

> To generate a secure random secret key, use the command `openssl rand -hex 32` (works on Linux and MacOS, on Windows you can use, for example, an [online generator](https://www.browserling.com/tools/random-hex) of such numbers for this purpose)
+ Run the server:
```
cd btc-app
uvicorn app:api --reload
```
+ Run tg_bot.py
+ Find your bot in telegram by username and write the command /start
+ Send a message to the bot 'Я в консоли', copy your id and assign it to the `tg_admin_id` variable in the `config.py` file

If you did everything according to the instructions, the bot should work
___

## Built With

* [FastAPI](https://fastapi.tiangolo.com)
* [PonyORM](https://ponyorm.org)
* [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
* [bit](https://github.com/ofek/bit)
* [uvicorn](https://www.uvicorn.org)
