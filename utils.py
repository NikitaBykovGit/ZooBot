from bs4 import BeautifulSoup
import requests
import time

class Parcer:
    @staticmethod
    def parse_about(url):
        html = requests.get(url, verify=False).content
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', class_='news-detail')
        return div.get_text('\n\n', strip=True)[:1423] + div.get_text('\n\n', strip=True)[1492:-24]

    @staticmethod
    def parce_animal_name(url):
        html = requests.get(url, verify=False).content
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', class_='section-page')
        return div.find('template').text

    @staticmethod
    def parce_animal_image(url):
        html = requests.get(url, verify=False).content
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', class_='section-page')
        image = div.find_all('img')[1]['src']
        image_req = requests.get('https://moscowzoo.ru' + image, verify=False)
        with open('AnimalImage.jpg', 'wb') as f:
            f.write(image_req.content)

class Animal:
    def __init__(self, element, diet, lifestyle, society, url=None):
        self.__element = element
        self.__diet = diet
        self.__lifestyle = lifestyle
        self.__society = society
        self.__url = url

    def __eq__(self, other):
        return (self.__element == other.element and self.__diet == other.diet and self.__lifestyle == other.lifestyle and
                self.__society == other.society)

    def __str__(self):
        return self.__element + ' ' + self.__diet + ' ' + self.__lifestyle + ' ' + self.__society

    @property
    def element(self):
        return self.__element

    @property
    def diet(self):
        return self.__diet

    @property
    def lifestyle(self):
        return self.__lifestyle

    @property
    def society(self):
        return self.__society

    @property
    def url(self):
        return self.__url

class AnimalFactory:
    def __init__(self, element_dict, diet_dict, lifestyle_dict, society_dict):
        self.reset()
        self.element_dict = element_dict
        self.diet_dict = diet_dict
        self.lifestyle_dict = lifestyle_dict
        self.society_dict = society_dict

    def set_сharact(self, value):
        if self.element is None:
            self.element = self.element_dict.get(value)
        else:
            if self.diet is None:
                self.diet = self.diet_dict.get(value)
            else:
                if self.lifestyle is None:
                    self.lifestyle = self.lifestyle_dict.get(value)
                else:
                    self.society = self.society_dict.get(value)

    def reset(self):
        self.element = None
        self.diet = None
        self.lifestyle = None
        self.society = None

    def create_animal(self):
        if self.element is not None:
            if self.diet is not None:
                if self.lifestyle is not None:
                    if self.society is not None:
                        return Animal(self.element, self.diet, self.lifestyle, self.society)

class AnimalFinder:
    @staticmethod
    def find_animal(current_animal, animals):
        for animal in animals:
            if current_animal == animal:
                return animal

class Question:
    def __init__(self, questions):
        self.index = 0
        self.total = len(questions)
        self.questions = questions

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.total:
            self.reset()
            raise StopIteration
        value = self.questions[self.index]
        self.index += 1
        return value

    def reset(self):
        self.index = 0

class LineManager:
    def __init__(self):
        self.__status = 0

    @property
    def status(self):
        return self.__status

    def open_line_feedback(self):
        self.__status = 1

    def open_line_employee(self):
        self.__status = 2

    def cancel_line(self):
        self.__status = 0

class BotLogger:
    @staticmethod
    def log_performance(func):
        def wrapper(args):
            start_time = time.time()
            func(args)
            with open('log.txt', 'a') as f:
                f.write(f'Пользователь {args.from_user.id} запустил {func.__name__}. Время выполнения: {time.time() - start_time}\n')
        return wrapper