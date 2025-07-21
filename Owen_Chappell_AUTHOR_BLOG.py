import sys
import os
import feedparser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QTabWidget, QListWidget, QPushButton,
    QListWidgetItem, QMessageBox, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QPixmap, QDesktopServices, QColor, QPainter
import pygame

# Fix for PyInstaller asset paths
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.mixer.init()

class AboutTab(QWidget):
    def __init__(self, bio_text, picture_paths, contact_info, tips_text):
        super().__init__()
        layout = QVBoxLayout()

        bio_label = QLabel(bio_text + "\n\n" + tips_text + "\n\n" + contact_info)
        bio_label.setWordWrap(True)
        layout.addWidget(bio_label)

        for pic_path in picture_paths:
            pixmap = QPixmap(resource_path(pic_path))
            if not pixmap.isNull():
                pic_label = QLabel()
                pic_label.setAlignment(Qt.AlignCenter)
                pic_label.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
                layout.addWidget(pic_label)

        layout.addStretch()
        self.setLayout(layout)

class BooksTab(QWidget):
    def __init__(self, books):
        super().__init__()
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        for book in books:
            title = book.get("title", "Untitled")
            price = book.get("price", "N/A")
            item = QListWidgetItem(f"{title} — ${price}")
            item.setData(Qt.UserRole, book)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        self.buttons_layout = QHBoxLayout()

        self.amazon_button = QPushButton("Buy on Amazon")
        self.amazon_button.clicked.connect(self.buy_amazon)
        self.buttons_layout.addWidget(self.amazon_button)

        self.google_play_button = QPushButton("Buy on Google Play")
        self.google_play_button.clicked.connect(self.buy_google_play)
        self.buttons_layout.addWidget(self.google_play_button)

        layout.addLayout(self.buttons_layout)
        self.setLayout(layout)

    def buy_amazon(self):
        item = self.list_widget.currentItem()
        if item:
            book = item.data(Qt.UserRole)
            url = book.get("amazon_link", "")
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                QMessageBox.information(self, "No Link", "No Amazon link provided for this book.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to buy.")

    def buy_google_play(self):
        item = self.list_widget.currentItem()
        if item:
            book = item.data(Qt.UserRole)
            url = book.get("google_play_link", "")
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                QMessageBox.information(self, "No Link", "No Google Play link provided for this book.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to buy.")

class BlogTab(QWidget):
    def __init__(self, rss_url):
        super().__init__()
        self.rss_url = rss_url
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.open_post)
        layout.addWidget(self.list_widget)

        self.refresh_button = QPushButton("Refresh Feed")
        self.refresh_button.clicked.connect(self.load_feed)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.load_feed()

    def load_feed(self):
        self.list_widget.clear()
        feed = feedparser.parse(self.rss_url)
        if feed.bozo:
            QMessageBox.critical(self, "Feed Error", "Failed to load RSS feed.")
            return
        for entry in feed.entries:
            title = entry.get('title', 'No title')
            summary = entry.get('summary', '')
            item = QListWidgetItem(title)
            item.setToolTip(summary)
            item.setData(Qt.UserRole, entry.get('link', ''))
            self.list_widget.addItem(item)

    def open_post(self, item):
        url = item.data(Qt.UserRole)
        if url:
            QDesktopServices.openUrl(QUrl(url))

class DontPressWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(100, 100, 600, 400)

        # Black button with no text
        self.button = QPushButton("")
        self.button.setStyleSheet("background-color: black; border: none;")
        self.button.clicked.connect(self.start_rainbow_and_music)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_background)
        self.rainbow_colors = [
            QColor(255, 0, 0),
            QColor(255, 127, 0),
            QColor(255, 255, 0),
            QColor(0, 255, 0),
            QColor(0, 0, 255),
            QColor(75, 0, 130),
            QColor(148, 0, 211),
        ]
        self.color_index = 0
        self.music_channel = None
        self.music = pygame.mixer.Sound(resource_path("assets/colleen_song.wav"))
        self.music.set_volume(1.0)
        self.is_rainbow_on = False

        self.text = "COLLEEN IS A LOSER AND A GROOMER"

    def start_rainbow_and_music(self):
        if not self.is_rainbow_on:
            self.is_rainbow_on = True
            self.timer.start(100)  # change color every 100ms
            if self.music_channel is None or not self.music_channel.get_busy():
                self.music_channel = self.music.play(loops=-1)
            self.button.hide()

    def update_background(self):
        self.color_index = (self.color_index + 1) % len(self.rainbow_colors)
        self.update()

    def paintEvent(self, event):
        if self.is_rainbow_on:
            painter = QPainter(self)
            painter.fillRect(self.rect(), self.rainbow_colors[self.color_index])
            painter.setPen(Qt.white)
            font = painter.font()
            font.setPointSize(20)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.text)

class OwenChappellAuthorBlog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Owen Chappell AUTHOR BLOG")
        self.resize(600, 700)

        bio_text = (
            "12 Year Old writer, I'm hoping my books will inspire other younger or older people "
            "to write books of their own, have a good day and remember \"YOU'RE AMAZING❤\""
        )

        tips_text = (
            "\n\n--- Tips and Inspiration for Authors ---\n"
            "- Write every day, even if it’s just a little.\n"
            "- Read widely and learn from others.\n"
            "- Don't be afraid to edit and revise.\n"
            "- Believe in your voice.\n"
            "- Connect with readers and other writers.\n"
            "- Take breaks to recharge your creativity.\n"
        )

        contact_info = (
            "\n\n--- Contact ---\n"
            "PHONE NUMBER: (469) 400-6663\n"
            "EMAIL: billlogan702@gmail.com"
        )

        picture_paths = ["assets/owen_chappell.png"]

        books = [
            {
                "title": "Colors: A Poem",
                "price": "5.99",
                "amazon_link": "https://www.amazon.com/Colors-Poem-Owen-Chappell-ebook/dp/B0F3VBCJZ9",
                "google_play_link": "https://play.google.com/store/books/details?id=X6VfEQAAQBAJ",
            },
            {
                "title": "Troubled",
                "price": "3.99",
                "amazon_link": "https://www.amazon.com/Troubled-Owen-Chappell-ebook/dp/B0F3RP29TP",
                "google_play_link": "https://play.google.com/store/books/details?id=F3ZfEQAAQBAJ",
            },
            {
                "title": "Witch's Life #1",
                "price": "4.99",
                "amazon_link": "https://www.amazon.com/Witchs-Life-1-Owen-Chappell-ebook/dp/B0F3S94Q3M",
                "google_play_link": "https://play.google.com/store/books/details?id=Y6VfEQAAQBAJ",
            },
            {
                "title": "Witch's Life #2",
                "price": "4.99",
                "amazon_link": "https://www.amazon.com/Witchs-Life-2-Owen-Chappell-ebook/dp/B0F3S67XTT",
                "google_play_link": "https://play.google.com/store/books/details?id=Z6VfEQAAQBAJ",
            },
            {
                "title": "Witch's Life #3",
                "price": "4.99",
                "amazon_link": "https://www.amazon.com/Witchs-Life-3-Owen-Chappell-ebook/dp/B0F3S9B2FW",
                "google_play_link": "https://play.google.com/store/books/details?id=b6VfEQAAQBAJ",
            },
            {
                "title": "Witch's Life #4",
                "price": "4.99",
                "amazon_link": "https://www.amazon.com/Witchs-Life-4-Owen-Chappell-ebook/dp/B0F3V7VKRL",
                "google_play_link": "https://play.google.com/store/books/details?id=caVfEQAAQBAJ",
            },
            {
                "title": "Shadow Book A Witch's Favorite Spells of Protection and Positivity",
                "price": "6.99",
                "amazon_link": "https://www.amazon.com/Shadow-Book-Protection-Positivity-WITCHCRAFT-ebook/dp/B0FJ4Q15FW",
                "google_play_link": "https://play.google.com/store/books/details?id=7U5yEQAAQBAJ",
            },
            {
                "title": "Shadow Book A Witch's Favorite Spells of Hexes and Curses",
                "price": "6.99",
                "amazon_link": "https://www.amazon.com/Shadow-Book-Witchs-Favorite-WITCHCRAFT-ebook/dp/B0FJ5L9P74",
                "google_play_link": "https://play.google.com/store/books/details?id=2VZyEQAAQBAJ",
            },
        ]

        rss_url = "https://www.spreaker.com/show/6689985/episodes/feed"

        tabs = QTabWidget()
        tabs.addTab(AboutTab(bio_text, picture_paths, contact_info, tips_text), "About Me")
        tabs.addTab(BooksTab(books), "My Books")
        tabs.addTab(BlogTab(rss_url), "Blog Feed")
        tabs.addTab(DontPressWindowTab(), "DONT PRESS")

        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

class DontPressWindowTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.button = QPushButton("")
        self.button.setStyleSheet("background-color: black; border: none;")
        self.button.clicked.connect(self.open_dont_press_window)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.window = None

    def open_dont_press_window(self):
        if self.window is None:
            self.window = DontPressWindow()
        self.window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OwenChappellAuthorBlog()
    window.show()
    sys.exit(app.exec_())
