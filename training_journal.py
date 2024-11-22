import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
import json
from datetime import datetime
import pandas as pd
from tkcalendar import DateEntry

# Файл для сохранения данных
data_file = 'out/training_log.json'
csv_file = 'out/training.csv'

def load_data():
    """Загрузка данных о тренировках из файла."""
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    """Сохранение данных о тренировках в файл."""
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)

class TrainingLogApp:
    def __init__(self, root):
        self.root = root
        root.title("Дневник тренировок")
        self.create_widgets()

    def create_widgets(self):

        self.exercise_label = ttk.Label(self.root, text="период")
        self.exercise_label.grid(column=0, row=0, sticky="new", padx=5, pady=5)

        self.date_begin = DateEntry(self.root)
        self.date_begin.grid(row=0, column=1, padx=10, pady=10,sticky="nesw")

        self.date_end = DateEntry(self.root)
        self.date_end.grid(row=0, column=2, padx=10, pady=10,sticky="nesw")
        # Виджеты для ввода данных
        self.exercise_label = ttk.Label(self.root, text="Упражнение:")
        self.exercise_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

        self.exercise_entry = ttk.Entry(self.root)
        self.exercise_entry.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5)

        self.weight_label = ttk.Label(self.root, text="Вес, в кг:")
        self.weight_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)

        self.weight_entry = ttk.Entry(self.root)
        self.weight_entry.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

        self.repetitions_label = ttk.Label(self.root, text="Повторения:")
        self.repetitions_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)

        self.repetitions_entry = ttk.Entry(self.root)
        self.repetitions_entry.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)

        self.add_button = ttk.Button(self.root,  text="Добавить      запись", command=self.add_entry)
        self.add_button.grid(column=0, row=6, columnspan=3, pady=5)

        self.view_button = ttk.Button(self.root, text="Просмотреть записи ", command=self.view_records)
        self.view_button.grid(column=0, row=7, columnspan=3, pady=5)

        self.view_button = ttk.Button(self.root, text="В CSV", command=self.to_csv)
        self.view_button.grid(column=0, row=8, columnspan=1, pady=5, padx=30)

        self.view_button = ttk.Button(self.root, text="Из CSV", command=self.from_csv)
        self.view_button.grid(column=1, row=8, columnspan=8, pady=5,padx=30)



    def add_entry(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exercise = self.exercise_entry.get()
        weight = self.weight_entry.get()
        repetitions = self.repetitions_entry.get()

        if not (exercise and weight and repetitions):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        entry = {
            'date': date,
            'exercise': exercise,
            'weight': weight,
            'repetitions': repetitions
        }

        data = load_data()
        data.append(entry)
        save_data(data)

        # Очистка полей ввода после добавления
        self.exercise_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.repetitions_entry.delete(0, tk.END)
        messagebox.showinfo("Успешно", "Запись успешно добавлена!")

    def view_records(self):
        data = load_data()


        start_date = self.date_begin.get_date()
        end_date = self.date_end.get_date()

        records_window = Toplevel(self.root)
        records_window.title("Записи тренировок")

        tree = ttk.Treeview(records_window, columns=("Дата", "Упражнение", "Вес", "Повторения"), show="headings")
        tree.heading('Дата', text="Дата")
        tree.heading('Упражнение', text="Упражнение")
        tree.heading('Вес', text="Вес")
        tree.heading('Повторения', text="Повторения")

        for entry in data:
            entry_date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S').date()
            if entry_date > start_date and entry_date < end_date:

                tree.insert('', tk.END, values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))

        tree.pack(expand=True, fill=tk.BOTH)

    def to_csv(self):
        data = load_data()
        # Создание DataFrame из словаря
        df = pd.DataFrame(data)

        # Экспорт DataFrame в CSV-файл
        df.to_csv(csv_file, index=False)
        messagebox.showinfo("Успех", "Данные успешно экспортированы в CSV файл.")

    def from_csv(self):
        # Чтение CSV-файла
        df = pd.read_csv(csv_file)

        # Преобразование DataFrame в словарь
        data = df.set_index('date').to_dict('index')
        messagebox.showinfo("Успех", "Данные успешно импортированы в CSV файл.")

def main():
    root = tk.Tk()
    app = TrainingLogApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
