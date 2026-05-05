import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "movies.json"

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # Данные
        self.movies = []
        self.load_data()

        # Виджеты
        self.create_input_frame()
        self.create_table()
        self.create_filter_frame()

        # Отобразить все фильмы
        self.refresh_table()

    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавить новый фильм", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Название
        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = tk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Жанр
        tk.Label(frame, text="Жанр:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.genre_entry = tk.Entry(frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5, pady=5)

        # Год
        tk.Label(frame, text="Год выпуска:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.year_entry = tk.Entry(frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Рейтинг
        tk.Label(frame, text="Рейтинг (0–10):").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.rating_entry = tk.Entry(frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Кнопка добавления
        self.add_btn = tk.Button(frame, text="Добавить фильм", command=self.add_movie, bg="lightgreen")
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=10)

    def create_table(self):
        frame = tk.LabelFrame(self.root, text="Список фильмов", padx=10, pady=10)
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

    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_genre_entry = tk.Entry(frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Фильтр по году:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_year_entry = tk.Entry(frame, width=10)
        self.filter_year_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame, text="Применить фильтр", command=self.apply_filter, bg="lightblue").grid(row=0, column=4, padx=10)
        tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter, bg="lightgray").grid(row=0, column=5, padx=10)

    def add_movie(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()

        # Валидация
        if not title or not genre or not year_str or not rating_str:
            messagebox.showerror("Ошибка", "Заполните все поля.")
            return

        try:
            year = int(year_str)
            if year < 1888 or year > 2100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть целым числом (1888–2100).")
            return

        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10.")
            return

        movie = {
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating
        }
        self.movies.append(movie)
        self.save_data()
        self.refresh_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

    def refresh_table(self, movie_list=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        movies_to_show = movie_list if movie_list is not None else self.movies
        for movie in movies_to_show:
            self.tree.insert("", tk.END, values=(movie["title"], movie["genre"], movie["year"], movie["rating"]))

    def apply_filter(self):
        genre_filter = self.filter_genre_entry.get().strip().lower()
        year_filter_str = self.filter_year_entry.get().strip()

        filtered = self.movies[:]

        if genre_filter:
            filtered = [m for m in filtered if genre_filter in m["genre"].lower()]

        if year_filter_str:
            try:
                year_filter = int(year_filter_str)
                filtered = [m for m in filtered if m["year"] == year_filter]
            except ValueError:
                messagebox.showerror("Ошибка", "Год для фильтра должен быть числом.")
                return

        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_year_entry.delete(0, tk.END)
        self.refresh_table()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except:
                self.movies = []
        else:
            self.movies = []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.movies, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()