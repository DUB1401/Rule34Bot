from telebot.types import InputMediaPhoto, InputMediaVideo
from dublib.Methods import ReadJSON, WriteJSON
from dublib.WebRequestor import WebRequestor
from dublib.Polyglot import Markdown, HTML
from telebot import TeleBot

import random
import os

# Менеджер бота.
class BotManager:
	
	# Строит описание.
	def __BuildCaption(self, Post: dict) -> str:
		# Текст подписи.
		Caption = str()
		# Список секций.
		Sections = ["artists", "characters", "fandoms", "tags"]
		# Определения эмодзи.
		Emoji = {
			"artists": "🖌️",
			"characters": "👥",
			"fandoms": "💥",
			"tags": "\n🔗"
		}
		
		# Для каждой секции.
		for Section in Sections:
			
			# Если указаны персонажи.
			if len(Post[Section]) > 0:
				# Составление названия секции.
				SectionName = self.__Settings["sections-names"][Section]
				
				# Если несколько значений
				if len(Post[Section]) > 1:
					# Запись во множественном числе.
					SectionName = SectionName.replace("|", "")
					
				else:
					# Запись в одиночном числе.
					SectionName = SectionName.split("|")[0]
					
				# Добавление названия секции.
				Caption += Emoji[Section] + " " + SectionName + "\: "
			
				# Для каждого сегмента.
				for Segment in Post[Section]:
					# Обработка сегмента.
					Segment = HTML(Segment).plain_text
					Segment = Segment.replace(" ", "_")
					Segment = Segment.replace("(", "")
					Segment = Segment.replace(")", "")
					Segment = Segment.replace("'", "")
					Segment = Segment.replace("-", "_")
					Segment = Segment.replace(":", "")
					Segment = Segment.replace("/", "")
					Segment = Segment.replace("\\", "")
					Segment = Segment.replace(".", "_")
					Segment = Segment.replace("<", "")
					Segment = Segment.replace(">", "")
					Segment = Segment.replace("=", "_")
					# Если сегмент не является число, влазит в сообщение и не пустой, добавить его.
					if Segment.isdigit() == False and len(Caption) < 1008 and Segment.strip(" _") != "": Caption += "\#" + Markdown(Segment).escaped_text + ", "
				
				# Очистка краевых символов.
				Caption = Caption.strip(", ")
				# Добавление новой строки.
				Caption += "\n"
			
		# Если есть источник, добавить его.
		if Post["source"] != None: Caption += "\n©️ [" + self.__Settings["sections-names"]["source"] + "](" + Post["source"] + ")"
		
		return Caption
			
	# Загружает файл.
	def __DownloadFile(self, URL: str, Type: str):
		# Удаление файла.
		if os.path.exists(f"Temp/File.{Type}"): os.remove(f"Temp/File.{Type}")
		# Запрос файла.
		Response = self.__Requestor.get(URL)
		
		# Если запрос успешен.
		if Response.status_code == 200:
			# Запись файла.
			with open(f"Temp/File.{Type}", "wb") as FileWriter: FileWriter.write(Response.content)
	
	# Помечает пост.
	def __MarkAs(self, PostID: int, Mark: str):
		# Удаление данных о посте.
		del self.__Posts["unsended"][str(PostID)]
		# Запись данных в список.
		self.__Posts[Mark].append(PostID)
		# Вычисление количества неотправленных постов.
		self.__Posts["unsended-count"] = len(self.__Posts["unsended"].keys())
		# Сохранение.
		WriteJSON("Data/Posts.json", self.__Posts)
		
	# Конструктор. 
	def __init__(self, settings: dict):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Описания постов.
		self.__Posts = ReadJSON("Data/Posts.json")
		# Глоабльные настройки.
		self.__Settings = settings.copy()
		# Запросчик.
		self.__Requestor = WebRequestor()
		# Экземпляр бота.
		self.__Bot = TeleBot(settings["token"])
		# Типы вложений.
		self.__Types = {
			"jpg": InputMediaPhoto,
			"mp4": InputMediaVideo
		}
		
		# Инициализация запросчика.
		self.__Requestor.initialize()
		
	# Отправляет пост.
	def send(self):
		
		# Если есть посты для отправки.
		if len(self.__Posts["unsended"].keys()) > 0 and os.path.exists("Data/blocked") == False:
				
			try:
				# ID поста.
				PostID = random.choice(list(self.__Posts["unsended"].keys())) if self.__Settings["random"] == True else list(self.__Posts["unsended"].keys())[0]
				# Описание поста.
				Post = self.__Posts["unsended"][PostID]
				# Скачивание файла.
				self.__DownloadFile(Post["url"], Post["type"])
				# Список медиафайлов.
				MediaGroup = list()
				# Построение описания.
				Caption = self.__BuildCaption(Post)
			
				# Если размер файла меньше 20 MB.
				if os.path.getsize("Temp/File." + Post["type"]) < 20971520:
					# Буфер.
					Bufer = self.__Types[Post["type"]](
						media = open("Temp/File." + Post["type"], "rb"),
						caption = Caption,
						parse_mode = "MarkdownV2"
					)
					# Добавление в список.
					MediaGroup.append(Bufer)

					# Отправка сообщения.
					self.__Bot.send_media_group(
						chat_id = self.__Settings["target"],
						media = MediaGroup
					)
					# Перемещение поста в список отправленных.
					self.__MarkAs(int(PostID), "sended")
				
				else:
					# Перемещение поста в список вызвавших ошибку.
					self.__MarkAs(int(PostID), "errors")
					
			except Exception as ExceptionData:
				# Приведение к строке.
				ExceptionData = str(ExceptionData)
				# Если изображение имеет неподдерживаемое разрешение.
				if "PHOTO_INVALID_DIMENSIONS" in ExceptionData: self.__MarkAs(int(PostID), "errors")
				# Вывод в консоль: исключение.
				print(ExceptionData)