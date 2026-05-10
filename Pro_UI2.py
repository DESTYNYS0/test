# Модуль для кодування зображення в base64
import base64

# Дозволяє працювати з байтами як з файлом в пам'яті
import io

# Для окремого потоку отримання повідомлень
import threading

# Імпорт сокетів для підключення до сервера
from socket import socket, AF_INET, SOCK_STREAM

# Потрібен для os.path.basename()
import os

# Імпорт всіх елементів CustomTkinter
from customtkinter import *

# Вікно вибору файлів
from tkinter import filedialog

# Робота із зображеннями
from PIL import Image


# Головне вікно програми
class MainWindow(CTk):

    # Конструктор класу
    def __init__(self):
        super().__init__()

        # Розмір головного вікна
        self.geometry('400x300')

        # Назва вікна
        self.title("Chat Client")

        # Ім'я користувача за замовчуванням
        self.username = "Artem"

        # ---------------- МЕНЮ ----------------

        # Спочатку label не існує
        self.label = None

        # Створення бокового меню
        self.menu_frame = CTkFrame(
            self,
            width=30,
            height=300
        )

        # Забороняє автоматично змінювати розмір frame
        self.menu_frame.pack_propagate(False)

        # Початкова позиція меню
        self.menu_frame.place(x=0, y=0)

        # Меню закрите
        self.is_show_menu = False

        # Швидкість анімації меню
        self.speed_animate_menu = -20

        # Кнопка відкриття/закриття меню
        self.btn = CTkButton(
            self,
            text='▶️',
            command=self.toggle_show_menu,
            width=30
        )
        self.btn.place(x=0, y=0)

        # ---------------- ЧАТ ----------------

        # Поле, де будуть показуватись повідомлення
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        # ---------------- ВВІД ПОВІДОМЛЕНЬ ----------------

        # Поле введення тексту
        self.message_entry = CTkEntry(
            self,
            placeholder_text='Введіть повідомлення:',
            height=40
        )
        self.message_entry.place(x=0, y=0)

        # Кнопка надсилання тексту
        self.send_button = CTkButton(
            self,
            text='>',
            width=50,
            height=40,
            command=self.send_message
        )
        self.send_button.place(x=0, y=0)

        # Кнопка відкриття картинки
        self.open_img_button = CTkButton(
            self,
            text='📂',
            width=50,
            height=40,
            command=self.open_image
        )
        self.open_img_button.place(x=0, y=0)

        # Запускаємо адаптивне оновлення інтерфейсу
        self.adaptive_ui()

        # Демонстраційне повідомлення із картинкою
        self.add_message(
            "Демонстрація відображення зображення:",
            CTkImage(
                Image.open('Screenshot_1.png'),
                size=(300, 300)
            )
        )

        # ---------------- ПІДКЛЮЧЕННЯ ДО СЕРВЕРА ----------------
        try:
            # Створюємо TCP сокет
            self.sock = socket(AF_INET, SOCK_STREAM)

            # Підключаємось до локального сервера
            self.sock.connect(('localhost', 8080))

            # Повідомлення про вхід користувача
            hello = (
                f"TEXT@{self.username}@"
                f"[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            )

            # Надсилаємо повідомлення серверу
            self.sock.send(hello.encode('utf-8'))

            # Окремий потік для отримання повідомлень
            threading.Thread(
                target=self.recv_message,
                daemon=True
            ).start()

        except Exception as e:
            # Якщо сервер недоступний
            self.add_message(
                f"Не вдалося підключитися до сервера: {e}"
            )

    # ---------------- ВІДКРИТТЯ/ЗАКРИТТЯ МЕНЮ ----------------
    def toggle_show_menu(self):

        if self.is_show_menu:
            # Закриваємо меню
            self.is_show_menu = False

            # Міняємо напрям анімації
            self.speed_animate_menu *= -1

            # Міняємо іконку кнопки
            self.btn.configure(text='▶️')

            self.show_menu()

        else:
            # Відкриваємо меню
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()

            # Текст "Ім'я"
            self.label = CTkLabel(
                self.menu_frame,
                text='Імʼя'
            )
            self.label.pack(pady=30)

            # Поле введення нового імені
            self.entry = CTkEntry(
                self.menu_frame,
                placeholder_text="Ваш нік..."
            )
            self.entry.pack()

            # Кнопка збереження нового імені
            self.save_button = CTkButton(
                self.menu_frame,
                text="Зберегти",
                command=self.save_name
            )
            self.save_button.pack()

    # Анімація меню
    def show_menu(self):

        # Змінюємо ширину меню
        self.menu_frame.configure(
            width=self.menu_frame.winfo_width() +
                  self.speed_animate_menu
        )

        # Якщо меню відкривається
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)

        # Якщо меню закривається
        elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
            self.after(10, self.show_menu)

            # Видаляємо елементи меню
            if self.label:
                self.label.destroy()

            if getattr(self, "entry", None):
                self.entry.destroy()

            if getattr(self, "save_button", None):
                self.save_button.destroy()

    # Збереження нового імені
    def save_name(self):
        new_name = self.entry.get().strip()

        if new_name:
            self.username = new_name
            self.add_message(
                f"Ваш новий нік: {self.username}"
            )

    # ---------------- АДАПТИВНИЙ UI ----------------
    def adaptive_ui(self):

        # Висота меню = висоті вікна
        self.menu_frame.configure(
            height=self.winfo_height()
        )

        # Позиція поля чату
        self.chat_field.place(
            x=self.menu_frame.winfo_width()
        )

        # Розмір поля чату
        self.chat_field.configure(
            width=self.winfo_width() -
                  self.menu_frame.winfo_width() - 20,

            height=self.winfo_height() - 40
        )

        # Кнопка відправки
        self.send_button.place(
            x=self.winfo_width() - 50,
            y=self.winfo_height() - 40
        )

        # Поле введення
        self.message_entry.place(
            x=self.menu_frame.winfo_width(),
            y=self.send_button.winfo_y()
        )

        # Ширина поля введення
        self.message_entry.configure(
            width=self.winfo_width() -
                  self.menu_frame.winfo_width() - 110
        )

        # Кнопка картинки
        self.open_img_button.place(
            x=self.winfo_width() - 105,
            y=self.send_button.winfo_y()
        )

        # Постійне оновлення UI
        self.after(50, self.adaptive_ui)

    # ---------------- ДОДАВАННЯ ПОВІДОМЛЕННЯ ----------------
    def add_message(self, message, img=None):

        # Контейнер одного повідомлення
        message_frame = CTkFrame(
            self.chat_field,
            fg_color='grey'
        )
        message_frame.pack(
            pady=5,
            anchor='w'
        )

        # Максимальна ширина тексту
        wrapleng_size = (
            self.winfo_width() -
            self.menu_frame.winfo_width() - 40
        )

        # Якщо це просто текст
        if not img:
            CTkLabel(
                message_frame,
                text=message,
                wraplength=wrapleng_size,
                text_color='white',
                justify='left'
            ).pack(padx=10, pady=5)

        else:
            # Якщо є картинка
            CTkLabel(
                message_frame,
                text=message,
                wraplength=wrapleng_size,
                text_color='white',
                image=img,
                compound='top',
                justify='left'
            ).pack(padx=10, pady=5)

    # ---------------- НАДСИЛАННЯ ТЕКСТУ ----------------
    def send_message(self):

        # Беремо текст
        message = self.message_entry.get()

        if message:
            # Показуємо локально
            self.add_message(
                f"{self.username}: {message}"
            )

            # Формат повідомлення
            data = f"TEXT@{self.username}@{message}\n"

            try:
                # Відправка серверу
                self.sock.sendall(
                    data.encode()
                )
            except:
                pass

        # Очищення поля
        self.message_entry.delete(0, END)

    # ---------------- ОТРИМАННЯ ПОВІДОМЛЕНЬ ----------------
    def recv_message(self):

        buffer = ""

        while True:
            try:
                chunk = self.sock.recv(4096)

                if not chunk:
                    break

                buffer += chunk.decode(
                    'utf-8',
                    errors='ignore'
                )

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break

        self.sock.close()

    # Обробка повідомлення
    def handle_line(self, line):

        if not line:
            return

        parts = line.split("@", 3)
        msg_type = parts[0]

        # Якщо текст
        if msg_type == "TEXT":

            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]

                self.add_message(
                    f"{author}: {message}"
                )

        # Якщо картинка
        elif msg_type == "IMAGE":

            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]

                try:
                    # Декодування картинки
                    img_data = base64.b64decode(
                        b64_img
                    )

                    pil_img = Image.open(
                        io.BytesIO(img_data)
                    )

                    ctk_img = CTkImage(
                        pil_img,
                        size=(300, 300)
                    )

                    self.add_message(
                        f"{author} надіслав(ла): {filename}",
                        img=ctk_img
                    )

                except Exception as e:
                    self.add_message(
                        f"Помилка картинки: {e}"
                    )

        else:
            self.add_message(line)

    # ---------------- ВІДПРАВКА ЗОБРАЖЕННЯ ----------------
    def open_image(self):

        # Вибір файлу
        file_name = filedialog.askopenfilename()

        if not file_name:
            return

        try:
            # Читаємо файл
            with open(file_name, "rb") as f:
                raw = f.read()

            # Кодуємо в base64
            b64_data = base64.b64encode(raw).decode()

            # Назва файлу
            short_name = os.path.basename(file_name)

            # Формуємо пакет
            data = (
                f"IMAGE@{self.username}@"
                f"{short_name}@{b64_data}\n"
            )

            # Відправляємо серверу
            self.sock.sendall(
                data.encode()
            )

            # Показуємо локально
            self.add_message(
                '',
                CTkImage(
                    light_image=Image.open(file_name),
                    size=(300, 300)
                )
            )

        except Exception as e:
            self.add_message(
                f"Не вдалося надіслати зображення: {e}"
            )


# Запуск програми
if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()