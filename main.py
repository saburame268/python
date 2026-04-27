import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Файл для хранения данных
DATA_FILE = "movies.json"

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.root.geometry("800x500")

        # Данные
        self.movies = self.load_movies()

        # Виджеты ввода
        self.create_input_frame()

        # Таблица для отображения
        self.create_treeview()

        # Фильтры
        self.create_filter_frame()

        # Кнопки управления
        self.create_button_frame()

        # Загрузка данных в таблицу
        self.refresh_table()

    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавить фильм", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_title = tk.Entry(frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Жанр:").grid(row=0, column=2, sticky="w")
        self.entry_genre = tk.Entry(frame, width=20)
        self.entry_genre.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Год:").grid(row=1, column=0, sticky="w")
        self.entry_year = tk.Entry(frame, width=10)
        self.entry_year.grid(row=1, column=1, padx=5)

        tk.Label(frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w")
        self.entry_rating = tk.Entry(frame, width=10)
        self.entry_rating.grid(row=1, column=3, padx=5)

    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтры", padx=5, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.filter_genre = tk.Entry(frame, width=20)
        self.filter_genre.grid(row=0, column=1, padx=5)
        self.filter_genre.bind("<KeyRelease>", lambda e: self.filter_movies())

        tk.Label(frame, text="Фильтр по году:").grid(row=0, column=2, sticky="w")
        self.filter_year = tk.Entry(frame, width=10)
        self.filter_year.grid(row=0, column=3, padx=5)
        self.filter_year.bind("<KeyRelease>", lambda e: self.filter_movies())

        tk.Button(frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=0, column=4, padx=10)

    def create_button_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Button(frame, text="Добавить фильм", command=self.add_movie, bg="lightgreen").pack(side="left", padx=5)
        tk.Button(frame, text="Удалить выбранный", command=self.delete_movie, bg="salmon").pack(side="left", padx=5)

    def create_treeview(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_movies(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_movies(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.movies, f, ensure_ascii=False, indent=4)

    def add_movie(self):
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year = self.entry_year.get().strip()
        rating = self.entry_rating.get().strip()

        if not title or not genre or not year or not rating:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return

        # Валидация года
        if not year.isdigit():
            messagebox.showerror("Ошибка", "Год должен быть числом")
            return
        year = int(year)

        # Валидация рейтинга
        try:
            rating = float(rating)
            if rating < 0 or rating > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10")
            return

        movie = {
            "название": title,
            "жанр": genre,
            "год": year,
            "рейтинг": rating
        }
        self.movies.append(movie)
        self.save_movies()
        self.refresh_table()

        # Очистка полей
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)

    def delete_movie(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления")
            return

        for item in selected:
            values = self.tree.item(item, "values")
            # Удаляем по названию и году (уникальная связка)
            for i, movie in enumerate(self.movies):
                if movie["название"] == values[0] and movie["год"] == int(values[2]):
                    del self.movies[i]
                    break

        self.save_movies()
        self.refresh_table()

    def filter_movies(self):
        genre_filter = self.filter_genre.get().strip().lower()
        year_filter = self.filter_year.get().strip()

        filtered = self.movies
        if genre_filter:
            filtered = [m for m in filtered if genre_filter in m["жанр"].lower()]
        if year_filter:
            if year_filter.isdigit():
                filtered = [m for m in filtered if m["год"] == int(year_filter)]
            else:
                messagebox.showerror("Ошибка", "Год для фильтрации должен быть числом")
                return

        self.refresh_table(filtered)

    def reset_filters(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self, movie_list=None):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        if movie_list is None:
            movie_list = self.movies

        for movie in movie_list:
            self.tree.insert("", "end", values=(
                movie["название"],
                movie["жанр"],
                movie["год"],
                movie["рейтинг"]
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()
