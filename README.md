# School project

Репозиторий для школьного проекта

## Структура
```
 .
├──  main.py - Основоной файл для запуска сервера
├──  pyproject.toml
├── 󰂺 README.md
├──  requirements.txt - Список зависимостей
└──  Source
    ├──  api - API, каждый файл кроме api.py - эндпоинт
    │   ├──  __init__.py
    │   ├──  api.py
    │   ├──  icon.py
    │   ├──  login_user.py
    │   ├──  refresh.py
    │   └──  register_user.py
    ├──  auth
    │   └──  token.py - Работа с JWT
    ├──  core
    │   └──  config.py - Работа с конфигом 
    ├──  database
    │   └──  database.py - Работа с БД
    ├──  Docs.md
    ├──  models - Pydantic модели для валидации данных
    │   ├──  __init__.py
    │   ├──  message.py
    │   └──  user.py 
    ├──  socket
    │   └──  my_socket.py - файл сокета
    └──  static
        └──  favicon.ico - Иконка для веб-сайта (плейсхолдер)
```
## Используемые технологии

+ JWT - Стандарт индустрии для одноразовых токенов
+ API - используется библиотека fastapi, архитекетура построена в соответствии со стандартами REST API
+ Websocket - Широко используемая библиотека для создания и поддержки постоянного канал связи между двумя устройствами
+ Textual - Фреймворк для создания TUI
+ Keyring для хранения чувствительных данных, таких как JWT-токен и Refresh token
