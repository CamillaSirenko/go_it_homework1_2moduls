import json
import datetime
from collections import UserDict
from abc import ABC, abstractmethod

class Field:
    def __init__(self, name, value):
        self.name = name
        self.__value = None
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        self.__value = value

    def __str__(self):
        return str(self.__value)

class Phone(Field):
    
    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        if not all(char.isdigit() for char in value):
            raise ValueError("Номер телефону повинен складатися лише з цифр")
        self.__value = value

class Birthday(Field):
    
    @property
    def value(self) -> datetime.date:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        if value is not None and not isinstance(value, datetime.date):
            raise ValueError("День народження повинен бути об'єктом datetime.date або None")
        self.__value = value

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def save_to_file(self, filename):
        with open(filename, 'w', encoding="utf-8") as file:
            data = {'contacts': self.data}
            json.dump(data, file, default=self.serialize_contact, ensure_ascii=False, indent=4)

    def serialize_contact(self, obj):
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        return obj.__dict__

    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                data = json.load(file)

            self.data = {}
            for name, contact in data['contacts'].items():
                name_field = Field("Ім'я", contact.get("Ім'я", ""))
                phone_field = Phone("Телефон", contact.get("Телефон", ""))
                birthday_string = contact.get("День народження", "")
                if birthday_string:
                    birthday_date = datetime.datetime.strptime(birthday_string, '%Y-%m-%d').date()
                else:
                    birthday_date = None  # Set to None when the date field is empty
                birthday_field = Birthday("День народження", birthday_date)

                contact_instance = Contact(name_field, phone_field, birthday_field)
                self.data[name] = contact_instance
        except FileNotFoundError:
            self.data = {}
        except UnicodeDecodeError:
            print(f"Error decoding file '{filename}' with UTF-8 encoding. Trying different encodings...")
            encodings_to_try = ["utf-16", "cp1251", "latin-1"]
            for encoding in encodings_to_try:
                try:
                    with open(filename, 'r', encoding=encoding) as file:
                        data = json.load(file)
                        self.data = {}
                        for name, contact in data['contacts'].items():
                            name_field = Field("Ім'я", contact.get("Ім'я", ""))
                            phone_field = Phone("Телефон", contact.get("Телефон", ""))
                            birthday_string = contact.get("День народження", "")
                            if birthday_string:
                                birthday_date = datetime.datetime.strptime(birthday_string, '%Y-%m-%d').date()
                            else:
                                birthday_date = None  # Set to None when the date field is empty
                            birthday_field = Birthday("День народження", birthday_date)

                            contact_instance = Contact(name_field, phone_field, birthday_field)
                            self.data[name] = contact_instance
                        print(f"File successfully decoded using encoding: {encoding}")
                        break
                except UnicodeDecodeError:
                    print(f"Failed to decode file using encoding: {encoding}")

    def search(self, query):
        query = query.lower()

        results = []

        for contact in self.data.values():
            contact_name = contact.name.value.lower()
            contact_phone = contact.optional_fields.get('Телефон', None)
            if contact_phone:
                contact_phone = contact_phone.value.lower()

            if query in contact_name or (contact_phone and query in contact_phone):
                results.append(contact)

        return results

class Record(ABC):
    @abstractmethod
    def display(self):
        pass

class Contact(Record):
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.optional_fields = {}
        if phone:
            self.add_phone(phone)
        if birthday:
            self.add_birthday(birthday)

    def display(self):
        print(f"Ім'я: {self.name.value}")
        for field_name, field in self.optional_fields.items():
            print(f"{field_name}: {field.value}")

    def add_field(self, field):
        if isinstance(field, Field):
            self.optional_fields[field.name] = field

    def remove_field(self, field_name):
        if field_name in self.optional_fields:
            del self.optional_fields[field_name]

    def edit_field(self, field_name, new_value):
        if field_name in self.optional_fields:
            self.optional_fields[field_name].value = new_value

    def add_phone(self, phone):
        if isinstance(phone, Phone):
            self.optional_fields['Телефон'] = phone

    def add_birthday(self, birthday):
        if isinstance(birthday, Birthday):
            self.optional_fields['День народження'] = birthday

    def days_to_birthday(self):
        if 'День народження' in self.optional_fields and self.optional_fields['День народження'].value:
            today = datetime.date.today()
            birthday = self.optional_fields['День народження'].value 
            next_birthday = datetime.date(today.year, birthday.month, birthday.day)
            if today > next_birthday:
                next_birthday = datetime.date(today.year + 1, birthday.month, birthday.day)
            days_remaining = (next_birthday - today).days
            return days_remaining

class UserInterface(ABC):

    @abstractmethod
    def display_menu(self):
        pass

    @abstractmethod
    def get_choice(self):
        pass

    @abstractmethod
    def display_results(self, results):
        pass

class ConsoleUserInterface(UserInterface):

    def display_menu(self):
        print("1. Додати контакт")
        print("2. Пошук контакту")
        print("3. Вийти")

    def get_choice(self):
        return input("Оберіть дію: ")

    def display_results(self, results):
        if results:
            print("Результати пошуку:")
            for contact in results:
                contact.display()
        else:
            print("Результати не знайдені.")

def main():
    ab = AddressBook()
    try:
        ab.load_from_file('my_contacts.json')
    except FileNotFoundError:
        pass

    ui = ConsoleUserInterface()

    while True:
        ui.display_menu()
        choice = ui.get_choice()

        if choice == '1':
            name_value = input("Введіть ім'я: ")
            phone_value = input("Введіть номер телефону: ")
            birthday_value = input("Введіть день народження (рррр-мм-дд): ")
            if birthday_value:
                birthday_date = datetime.datetime.strptime(birthday_value, '%Y-%m-%d').date()
            else:
                birthday_date = None  # Set to None when the date field is empty

            name = Field("Ім'я", name_value)
            phone = Phone("Телефон", phone_value)
            birthday = Birthday("День народження", birthday_date)
            contact = Contact(name, phone=phone, birthday=birthday)
            ab.add_record(contact)
            ab.save_to_file('my_contacts.json')
            print("Контакт успішно доданий та збережений.")

        elif choice == '2':
            search_query = input("Введіть пошуковий запит: ")
            search_results = ab.search(search_query)
            ui.display_results(search_results)

        elif choice == '3':
            break

        else:
            print("Невірний вибір. Спробуйте знову.")

    print("Програма завершена.")

if __name__ == "__main__":
    main()


