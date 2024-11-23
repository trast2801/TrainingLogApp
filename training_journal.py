import tkinter as tk
from tkinter import ttk, Toplevel, messagebox, simpledialog
import json
from datetime import datetime
import pandas as pd
from tkcalendar import DateEntry
import re
import matplotlib.pyplot as plt
import seaborn as sns


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

        def is_valid(newval):
            return re.match("\d", newval) is not None

        self.exercise_label = ttk.Label(self.root, text="период")
        self.exercise_label.grid(column=0, row=0, sticky="new", padx=5, pady=5)

        self.date_begin = DateEntry(self.root)
        self.date_begin.grid(row=0, column=1, padx=10, pady=10, sticky="nesw")

        self.date_end = DateEntry(self.root)
        self.date_end.grid(row=0, column=2, padx=10, pady=10, sticky="nesw")
        # Виджеты для ввода данных
        self.exercise_label = ttk.Label(self.root, text="Упражнение:")
        self.exercise_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)

        self.exercise_combobox = ttk.Combobox(self.root, values=self.list_exercise())
        self.exercise_combobox.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

        # self.exercise_entry = ttk.Entry(self.root)
        # self.exercise_entry.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

        self.weight_label = ttk.Label(self.root, text="Вес, в кг:")
        self.weight_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)

        check = (self.root.register(is_valid), "%P")
        self.weight_entry = ttk.Entry(self.root, validate="key", validatecommand=check)
        self.weight_entry.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)

        self.repetitions_label = ttk.Label(self.root, text="Повторения:")
        self.repetitions_label.grid(column=0, row=6, sticky=tk.W, padx=5, pady=5)

        self.repetitions_entry = ttk.Entry(self.root, validate="key", validatecommand=check)
        self.repetitions_entry.grid(column=1, row=6, sticky=tk.EW, padx=5, pady=5)

        self.add_button = ttk.Button(self.root, text="Добавить      запись", command=self.add_entry)
        self.add_button.grid(column=0, row=7, columnspan=3, pady=5)

        self.view_button = ttk.Button(self.root, text="Просмотреть записи ", command=self.view_records)
        self.view_button.grid(column=0, row=8, columnspan=3, pady=5)

        self.view_button = ttk.Button(self.root, text="Показать статистику ", command=self.show_statistics)
        self.view_button.grid(column=0, row=9, columnspan=3, pady=5)

        self.view_button = ttk.Button(self.root, text="График прогресса ", command=self.grafik)
        self.view_button.grid(column=0, row=10, columnspan=3, pady=5)

        self.view_button = ttk.Button(self.root, text="В CSV", command=self.to_csv)
        self.view_button.grid(column=0, row=11, columnspan=1, pady=5, padx=30)

        self.view_button = ttk.Button(self.root, text="Из CSV", command=self.from_csv)
        self.view_button.grid(column=2, row=11, columnspan=2, pady=5, padx=30)

    def add_entry(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exercise = self.exercise_combobox.get()
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
        self.exercise_combobox.delete(0, tk.END)
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

        vsb = ttk.Scrollbar(records_window, orient="vertical", command=tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        tree.configure(yscrollcommand=vsb.set)

        for entry in data:
            entry_date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S').date()
            if entry_date >= start_date and entry_date <= end_date:
                if entry['exercise'] == self.exercise_combobox.get():
                    tree.insert('', tk.END,
                                values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))
                elif self.exercise_combobox.get() == '':
                    tree.insert('', tk.END,
                                values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))

        tree.pack(expand=True, fill=tk.BOTH)

        def write_change():
            '''сохраняет в json файл изменения в tree'''
            values = []
            for k in tree.get_children(""):
                item = tree.item(k)
                values.append(item['values'])

            data = pd.DataFrame(values)
            data.columns = ['date', 'exercise', 'weight', 'repetitions']
            data.to_json(data_file, orient='table', lines=True)

        def update_item():
            '''редактирует выбранную запись '''
            selected = tree.focus()
            temp = tree.item(selected, 'values')

            column1 = simpledialog.askstring(" ", "Введите упражнение:", initialvalue=temp[1])
            column2 = simpledialog.askstring(" ", "Введите вес:", initialvalue=temp[2])
            column3 = simpledialog.askstring(" ", "Введите повтор:", initialvalue=temp[3])
            # Обновляем строку с новым значением
            values = (temp[0], column1, column2, column3)
            tree.item(selected, values=values)
            write_change()

        def save_after_delete():
            '''сохраняет список после удаления в файл'''
            delete_item()
            write_change()

        def delete_item():

            # удаляет запись из tree
            selected_item = tree.selection()[0]
            tree.delete(selected_item)

            ttk.Button(records_window, text='изменить запись', command=update_item).pack()
            ttk.Button(records_window, text='удалить запись', command=save_after_delete).pack()


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
        # data = df.set_index('date').to_dict('index')
        # Экспорт DataFrame в json-файл
        df.to_json(data_file, orient='records', lines=False)
        messagebox.showinfo("Успех", "Данные успешно импортированы в CSV файл.")

    def list_exercise(self) -> set:
        '''функция отбирает только уникальные упражнения для фильтрации в последующем выводе '''
        data = load_data()
        exercises = []
        for entry in data:
            exercises.append(entry['exercise'])
        exercises = list(set(exercises))
        return exercises

    def validate_number(P):
        """Функция для проверки, является ли введённое значение числом."""
        if P.isdigit() or P == "":
            return True
        return False

    def show_statistics(self):
        '''Фуункция вывода статистики по упражнениям'''
        df = pd.read_json(data_file)
        # Количество выполненных упражнений
        exercises_count = df['exercise'].value_counts().to_dict()

        # Суммарное количество повторений по каждому упражнению
        repetitions_sum = df.groupby('exercise')['repetitions'].sum().to_dict()

        # Средняя нагрузка (вес * повторения) по каждому виду упражнения
        load_avg = (df.groupby('exercise').apply(lambda x: (x['weight'] * x['repetitions']).mean())).to_dict()

        # Среднее количество повторений для каждого вида упражнения
        reps_avg = df.groupby('exercise')['repetitions'].mean().to_dict()

        # Форматируем данные для отображения
        rows = []
        for exercise, count in exercises_count.items():
            row = {
                'Упражнение': exercise,
                'Количество выполнений': count,
                'Сумма повторений': repetitions_sum[exercise],
                'Средняя нагрузка': round(load_avg[exercise], 2),
                'Среднее количество повторений': round(reps_avg[exercise], 2)
            }
            rows.append(row)

        # Создаем DataFrame для отображения
        stats_df = pd.DataFrame(rows)

        # Показываем статистику в отдельном окне Tkinter
        stat_window = tk.Toplevel()
        stat_window.title("Статистика")

        tree = ttk.Treeview(stat_window, columns=list(stats_df.columns), show='headings')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(stat_window, orient="vertical", command=tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        tree.configure(yscrollcommand=vsb.set)

        for col in stats_df.columns:
            tree.heading(col, text=col)

        for index, row in stats_df.iterrows():
            tree.insert("", "end", values=list(row))

    def grafik(self):
        '''Функция отражает график по весами по повторениям вразрезе дней и упражнений'''
        df = pd.read_json('out/training_log.json')
        start_date = self.date_begin.get_date()
        end_date = self.date_end.get_date()
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Преобразуем дату в формат datetime
        df['date'] = pd.to_datetime(df['date'],  format='%Y-%m-%d %H:%M:%S')
        filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        # Создадим отдельные датафреймы для веса и повторений
        weight_df = filtered_df.pivot(index='date', columns='exercise', values='weight')
        reps_df = filtered_df.pivot(index='date', columns='exercise', values='repetitions')

        # Постороим график изменения веса по упражнениям
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=weight_df, dashes=False)
        plt.title('График изменения веса по упражнениям')
        plt.xlabel('Дата')
        plt.ylabel('Вес')
        plt.legend(title='Упражнения')
        plt.show()

        # Постороим график изменения количества повторений по упражнениям
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=reps_df, dashes=False)
        plt.title('График изменения количества повторений по упражнениям')
        plt.xlabel('Дата')
        plt.ylabel('Повторения')
        plt.legend(title='Упражнения')
        plt.show()


def main():
    root = tk.Tk()
    app = TrainingLogApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
