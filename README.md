![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

### **Учебный проект Telegram bot**
Telegram bot отслеживания статуса отправленной на ревью домашней работы и присылает уведомлении.

#### **Установка**
Клонируем репозиторий:
```python
git@github.com:Maksim1301/homework_bot.git
```
Cоздать и активировать виртуальное окружение:

```python
python3 -m venv env
```
```python
source env/bin/activate
```
```python
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```python
pip install -r requirements.txt
```
Создаем .env файл с токенами:
```python
PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>
```
Запускаем бота:
```python
python homework.py
```
