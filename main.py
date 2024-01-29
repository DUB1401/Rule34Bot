from dublib.Methods import CheckPythonMinimalVersion, Cls, MakeRootDirectories, ReadJSON, Shutdown, WriteJSON
from dublib.Terminalyzer import ArgumentsTypes, Command, Terminalyzer
from Source.BotManager import BotManager
from Source.Parser import Parser

import logging
import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Temp"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Запись в лог сообщения: заголовок подготовки скрипта к работе.
logging.info("====== Preparing to starting ======")
# Запись в лог используемой версии Python.
logging.info("Starting with Python " + str(sys.version_info.major) + "." + str(sys.version_info.minor) + "." + str(sys.version_info.micro) + " on " + str(sys.platform) + ".")
# Запись команды, использовавшейся для запуска скрипта.
logging.info("Launch command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")
# Чтение настроек.
Settings = ReadJSON("Settings.json")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: clear.
COM_clear = Command("clear")
COM_clear.add_flag_position(["id", "unsended", "sended", "errors"])
COM_clear.add_flag_position(["s"])
CommandsList.append(COM_clear)

# Создание команды: parse.
COM_parse = Command("parse")
COM_parse.add_argument(ArgumentsTypes.All, important = True, layout_index = 1)
COM_parse.add_flag_position(["new"], important = True, layout_index = 1)
COM_parse.add_flag_position(["s"])
CommandsList.append(COM_parse)

# Создание команды: send.
COM_send = Command("send")
COM_send.add_flag_position(["s"])
CommandsList.append(COM_send)

# Создание команды: unblock.
COM_unblock = Command("unblock")
COM_unblock.add_flag_position(["s"])
CommandsList.append(COM_unblock)

# Инициализация обработчика консольных аргументов.
CAC = Terminalyzer()
# Получение информации о проверке команд.
CommandDataStruct = CAC.check_commands(CommandsList)

# Если не удалось определить команду, завершить скрипт с кодом ошибки.
if CommandDataStruct == None: exit(1)
	
#==========================================================================================#
# >>>>> ОБРАБОТКА СПЕЦИАЛЬНЫХ ФЛАГОВ <<<<< #
#==========================================================================================#

# Активна ли опция выключения компьютера по завершении работы парсера.
IsShutdowAfterEnd = False
# Сообщение для внутренних функций: выключение ПК.
InFuncMessage_Shutdown = ""

# Обработка флага: выключение ПК после завершения работы скрипта.
if "s" in CommandDataStruct.flags:
	# Включение режима.
	IsShutdowAfterEnd = True
	# Установка сообщения для внутренних функций.
	InFuncMessage_Shutdown = "Computer will be turned off after the script is finished!\n"
	
#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: clear.
if "clear" == CommandDataStruct.name:
	# Чтение файла.
	Data = ReadJSON("Data/Posts.json")

	# Если указано парсить новые посты.
	if len(CommandDataStruct.flags) == 0:
		# Очитска всех полей.
		Data["last-post-id"] = None
		Data["unsended-count"] = 0
		Data["unsended"] = dict()
		Data["sended"] = list()
		Data["errors"] = list()
		
	# Если указано парсить новые посты.
	if "id" in CommandDataStruct.flags:
		# Очитска поля.
		Data["last-post-id"] = None
		
	# Если указано парсить новые посты.
	if "unsended" in CommandDataStruct.flags:
		# Очитска полей.
		Data["unsended-count"] = 0
		Data["unsended"] = dict()
		
	# Если указано парсить новые посты.
	if "sended" in CommandDataStruct.flags:
		# Очитска поля.
		Data["sended"] = list()
		
	# Если указано парсить новые посты.
	if "errors" in CommandDataStruct.flags:
		# Очитска поля.
		Data["errors"] = list()
	
	# Сохранение файла.
	WriteJSON("Data/Posts.json", Data)

# Обработка команды: parse.
if "parse" == CommandDataStruct.name:
	# Инициализация парсера.
	ParserObject = Parser(Settings)
	
	try:

		# Если указано парсить новые посты.
		if "new" in CommandDataStruct.flags:
			# Получение списка обновлений.
			Updates = ParserObject.get_new_posts_id()
			# Парсинг конкретного поста.
			ParserObject.parse_posts(Updates)
	
		else:
			# Парсинг конкретного поста.
			ParserObject.parse_posts(int(CommandDataStruct.arguments[0]))
			
	except Exception as ExceptionData:
		# Вывод в консоль: исключение.
		print(ExceptionData)
	
	# Удаление файла блокировки.
	ParserObject.unblock()
		
# Обработка команды: send.
if "send" == CommandDataStruct.name:
	# Обработчик бота.
	BotProcessor = BotManager(Settings)
	# Отправка сообщения.
	BotProcessor.send()
	
# Обработка команды: unblock.
if "unblock" == CommandDataStruct.name:
	# Инициализация парсера.
	ParserObject = Parser(Settings)
	# Удаление файла блокировки.
	ParserObject.unblock()

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА <<<<< #
#==========================================================================================#

# Если указано, выключить компьютер.
if IsShutdowAfterEnd == True: Shutdown()