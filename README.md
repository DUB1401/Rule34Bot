# Rule34Bot
**Rule34Bot** – это бот, транслирующий посты с сайта [R-34.xyz](https://r-34.xyz/) в группу или канал [Telegram](https://telegram.org/) с автоматической простановкой тегов и форматированием.

## Порядок установки и использования
1. Загрузить последний релиз. Распаковать.
2. Установить Python версии не старше 3.10.
3. В среду исполнения установить следующие пакеты: [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI?ysclid=loq3f2bmuz181940716), [beautifulsoup4](https://launchpad.net/beautifulsoup), [dublib](https://github.com/DUB1401/dublib).
```
pip install pyTelegramBotAPI
pip install beautifulsoup4
pip install dublib
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_.
5. Назначить бота администратором группы или канала.
6. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
7. Выполнить последовательно команды для парсинга и отправки поста в Telegram.
8. Автоматизация процесса производится при помощи сторонних утилит, таких как **crond** в Linux или **Планировщик задач** в Windows.

# Консольные команды
```
clear [FIELD]
```
Очищает поля в файле _Posts.json_. При отстутсвии флага очищает сразу все поля. 

**Описание позиций:**
* **FIELD** – ключ поля, в котором необходимо сбросить значение.
	* Флаги:
		* _**-errors**_ – указывает для сброса поле _errors_;
		* _**-id**_ – указывает для сброса поле _id_;
		* _**-sended**_ – указывает для сброса поле _sended_;
		* _**-unsended**_ – указывает для сброса поле _unsended_.
___
```
parse [TARGET*]
```
Парсит один пост или получает все обновления и помещает их в файл _Posts.json_.

**Описание позиций:**
* **TARGET** – цель для парсинга. Обязательная позиция.
	* Аргмуент – ID поста.
	* Флаги:
		* _**-new**_ – указывает, что нужно спарсить все обновления на сайте (если файл _Posts.json_ пуст, будут получены последние 30 постов).
___
```
send
```
Формирует пост и отправляет его в группу или канал Telegram. Имеет следующие правила:

1. Теги, не умещающиеся в лимит 1024 символов, будут удалены.
2. Максимальный размер вложения – 20 MB. ID постов, имеющих больший размер, будут помещены в поле _errors_.
___
```
unblock
```
Удаляет файл _blocked_, использующийся для запрета отправки сообщений во время парсинга.

# Settings.json
```JSON
"token": ""
```
Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).
___
```JSON
"target": ""
```
Сюда необходимо занести ID канала Telegram (можно получить у [Chat ID Bot](https://t.me/chat_id_echo_bot)).
___
```JSON
"random": false
```
Если позиция активна, то бот будет отправлять случайный пост, иначе – первый в порядке убывания ID.
___
```JSON
"sections-names": {
	"artists": "Автор|ы",
	"characters": "Персонаж|и",
	"fandoms": "Фэндом|ы",
	"tags": "Тег|и",
	"source": "Источник"
}
```
Указывает названия секций. Через символ прямой черты можно задать окончание, отбрасываемое в случае, если за названием секции следует только один тег (исключение – _source_).
___
```JSON
"delay": 1
```
Задаёт интервал в секундах для паузы между запросами к сайту.

_Copyright © DUB1401. 2024._
