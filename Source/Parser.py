from dublib.Methods import Cls, ReadJSON, WriteJSON
from dublib.WebRequestor import WebRequestor
from bs4 import BeautifulSoup
from time import sleep

import json
import os

# Парсер изображений.
class Parser:
	
	# Создаёт файл блокировки.
	def __CreateBlockFile(self):
		# Создание пустого файла.
		with open("Data/blocked", "wb"): pass
	
	# Возвращает словарь классификаторов.
	def __GetClassificators(self, PostID: int) -> dict:
		# Запрос всех классификаторов.
		Response = self.__Requestor.get(f"https://r-34.xyz/api/post/{PostID}")
		# Словарь классификаторов.
		Classificators = {
			"artists": [],
			"characters": [],
			"fandoms": [],
			"tags": []
		}
		# Определения классификаторов.
		Determinations = {
			1: "tags",
			2: "fandoms",
			4: "characters",
			8: "artists"
		}
		
		# Если запрос успешен.
		if Response.status_code == 200:
			# Преобразование ответа в словарь.
			Data = json.loads(Response.text)
			
			# Для каждого классификатора.
			for Item in Data["fullTags"]:
				# Если присутствует определение, записать название классификатора.
				if Item["type"] in Determinations.keys(): Classificators[Determinations[Item["type"]]].append(Item["value"])
		
		return Classificators
	
	# Возвращает структуру поста.
	def __GetPost(self, post_id: int) -> dict | None:
		# Запрос поста.
		Response = self.__Requestor.get(f"https://r-34.xyz/post/{post_id}")
		# Буфер поста.
		Post = None
		
		# Если запрос успешен.
		if Response.status_code == 200:
			# Парсинг страницы.
			Soup = BeautifulSoup(Response.text, "html.parser")
			# Поиск видео.
			Video = Soup.find("video", {"id": "post-video"})
			# Получение классификаторов.			
			Classificators = self.__GetClassificators(post_id)
			# Буфер поста.
			Post = {
				"url": None,
				"type": None,
				"artists": sorted(Classificators["artists"]),
				"characters": sorted(Classificators["characters"]),
				"fandoms": sorted(Classificators["fandoms"]),
				"tags": sorted(Classificators["tags"]),
				"source": self.__GetSource(Soup)
			}
				
			# Если не удалось найти изображение.
			if Video != None:
				# Определение новой ссылки.
				URL = Video.find_all("source")[-1]
				
			else:
				# Поиск ссылки на файл.
				URL = Soup.find("img", {"class": "img"})
				
			# Получение ссылки.
			Post["url"] = URL["src"].replace("thumbnailex.", "")
			if Post["url"].startswith("https") == False: Post["url"] = "https://r-34.xyz" + Post["url"]
			# Запись расширения.
			Post["type"] = Post["url"].split(".")[-1]
			
		return Post
	
	# Возвращает источник
	def __GetSource(self, Page: BeautifulSoup) -> str | None:
		# Поиск ссылок в новую вкладку.
		Links = Page.find_all("a", {"target": "_blank"})
		# Ссылка на источник.
		Source = None
		# Если ссылка найдена, получить адрес.
		if len(Links) > 1: Source = Links[1]["href"]
		
		return Source

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
		
		# Инициализация запросчика.
		self.__Requestor.initialize()
		# Блокировка отправки.
		self.__CreateBlockFile()
		
	# Возвращает ID первого поста.
	def get_first_post_id(self) -> int | None:
		# ID первого поста.
		FirstID = None
		# Данные запроса.
		RequestData = {
			"status": 2,
			"sortOrder": 1,
			"blacklistType": 1,
			"take": 30,
			"cursor": None
		}
		# Запрос данных.
		Response = self.__Requestor.post("https://r-34.xyz/api/post/search/root", json = RequestData)
		
		# Если запрос успешен.
		if Response.status_code == 200:
			# Парсинг ответа в словарь.
			ResponseData = json.loads(Response.text)
			# Запись первого ID.
			FirstID = ResponseData["items"][0]["id"]
			
		return FirstID
		
	# Возвращает список ID новых постов.
	def get_new_posts_id(self) -> list[int]:
		# Состояние: не найден последний ID.
		IsLastNotFound = True if self.__Posts["last-post-id"] == None else False
		# ID первого поста.
		FirstID = self.get_first_post_id()
		# ID последнего сохранённого поста.
		LastID = self.__Posts["last-post-id"] if self.__Posts["last-post-id"] != None else 0
		# Индекс страницы.
		Index = 0
		# Список ID новых постов.
		NewPosts = list()
		# Состояние: завершён ли парсинг.
		IsParsed = False

		# Постоянно.
		while IsParsed == False:
			# Данные запроса.
			RequestData = {
				"status": 2,
				"sortOrder": 1,
				"blacklistType": 1,
				"take": 30,
				"cursor": FirstID - 30 * Index
			}
			# Инкремент индекса.
			Index += 1
			# Запрос данных.
			Response = self.__Requestor.post("https://r-34.xyz/api/post/search/root", json = RequestData)

			# Если запрос успешен.
			if Response.status_code == 200:
				# Парсинг ответа в словарь.
				ResponseData = json.loads(Response.text)
				
				# Для каждого поста.
				for Item in ResponseData["items"]:
					# Если пост новый или не найден последний ID, записать ID.
					if Item["id"] > LastID or IsLastNotFound == True: NewPosts.append(Item["id"])
					
					# Если пост не новый.
					if Item["id"] <= LastID: 
						# Переключение статуса.
						IsParsed = True
						# Остановка цикла.
						break
					
				# Если нужно было парсить одну страницу.
				if IsLastNotFound == True: break
				# Выжидание интервала.
				sleep(self.__Settings["delay"])
				
			# Очистка консоли.
			Cls()
			# Вывод в консоль: прогресс получения обновлений.
			print("Posts found: " + str(len(NewPosts)) + f"\nScanning page {Index}...")
				
		return NewPosts
		
	# Парсит посты.
	def parse_posts(self, posts_id: list[int] | int, UpdateLastID: bool = True):
		# Если указан один ID, преобразовать его в список.
		if type(posts_id) == int: posts_id = [posts_id]
		# Последний ID.
		LastID = max(posts_id)
		
		# Для каждого поста.
		for PostID in posts_id:
			# Очистка консоли.
			Cls()
			# Вывод в консоль: парсинг.
			print(f"Parsing post with ID {PostID}...")
			# Запрос поста.
			Post = self.__GetPost(PostID)
			
			# Если пост получен и не описан.
			if Post != None and str(PostID) not in self.__Posts["unsended"].keys() and PostID not in self.__Posts["sended"] and PostID not in self.__Posts["errors"]:
				# Запись поста.
				self.__Posts["unsended"][str(PostID)] = Post

		# Запись последнего ID.
		if UpdateLastID == True: self.__Posts["last-post-id"] = LastID
		# Сортировка записей.
		self.__Posts["unsended"] = dict(sorted(self.__Posts["unsended"].items(), reverse = True))
		self.__Posts["sended"] = sorted(self.__Posts["sended"], reverse = True)
		self.__Posts["errors"] = sorted(self.__Posts["errors"], reverse = True)
		# Сохранение файла постов.
		WriteJSON("Data/Posts.json", self.__Posts)
		
	# Удаляет файл блокировки.
	def unblock(self):
		# Удаление файла.
		if os.path.exists("Data/blocked") == True: os.remove("Data/blocked")