import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
from tkcalendar import DateEntry  # Нужно установить: pip install tkcalendar

FILE_NAME = "tasks.txt"

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("800x600")
        
        # Загрузка задач
        self.tasks = self.load_tasks()
        
        # Стили
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление отображения
        self.refresh_task_list()
        
    def setup_styles(self):
        self.root.configure(bg='#f0f0f0')
        
    def create_widgets(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#4a6fa5', height=80)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📋 To-Do List",
            font=('Arial', 24, 'bold'),
            bg='#4a6fa5',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Левая панель - добавление задачи
        left_panel = tk.Frame(main_container, bg='#ffffff', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        add_label = tk.Label(
            left_panel,
            text="Добавить новую задачу",
            font=('Arial', 14, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        add_label.pack(pady=20)
        
        # Поле для текста задачи
        tk.Label(left_panel, text="Описание задачи:", bg='#ffffff', anchor='w').pack(fill=tk.X, padx=20, pady=(0, 5))
        self.task_text = tk.Text(left_panel, height=4, width=30, font=('Arial', 11))
        self.task_text.pack(padx=20, pady=(0, 20))
        
        # Поле для даты
        tk.Label(left_panel, text="Дедлайн:", bg='#ffffff', anchor='w').pack(fill=tk.X, padx=20, pady=(0, 5))
        self.date_entry = DateEntry(
            left_panel,
            width=20,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Arial', 11)
        )
        self.date_entry.pack(padx=20, pady=(0, 20))
        
        # Кнопка добавления
        add_button = tk.Button(
            left_panel,
            text="➕ Добавить задачу",
            command=self.add_task_gui,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        add_button.pack(pady=20)
        
        # Правая панель - список задач
        right_panel = tk.Frame(main_container, bg='#ffffff', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заголовок списка
        list_header = tk.Frame(right_panel, bg='#e8e8e8', height=50)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)
        
        tk.Label(
            list_header,
            text="Список задач",
            font=('Arial', 16, 'bold'),
            bg='#e8e8e8',
            fg='#333333'
        ).pack(side=tk.LEFT, padx=20)
        
        # Поиск
        search_frame = tk.Frame(list_header, bg='#e8e8e8')
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(search_frame, text="Поиск:", bg='#e8e8e8').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_tasks_gui)
        
        # Список задач (Treeview)
        self.create_task_tree(right_panel)
        
        # Панель кнопок управления
        self.create_control_buttons(right_panel)
        
    def create_task_tree(self, parent):
        # Создаем Treeview с прокруткой
        tree_frame = tk.Frame(parent, bg='#ffffff')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Полосы прокрутки
        scroll_y = tk.Scrollbar(tree_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.task_tree = ttk.Treeview(
            tree_frame,
            columns=('Status', 'Task', 'Deadline', 'State'),
            show='tree headings',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode='browse'
        )
        
        # Настройка колонок
        self.task_tree.heading('#0', text='#')
        self.task_tree.column('#0', width=50, anchor='center')
        
        self.task_tree.heading('Status', text='Статус')
        self.task_tree.column('Status', width=100, anchor='center')
        
        self.task_tree.heading('Task', text='Задача')
        self.task_tree.column('Task', width=300, anchor='w')
        
        self.task_tree.heading('Deadline', text='Дедлайн')
        self.task_tree.column('Deadline', width=150, anchor='center')
        
        self.task_tree.heading('State', text='Состояние')
        self.task_tree.column('State', width=150, anchor='center')
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        scroll_y.config(command=self.task_tree.yview)
        scroll_x.config(command=self.task_tree.xview)
        
        # Привязка событий
        self.task_tree.bind('<Double-Button-1>', self.on_task_double_click)
        
    def create_control_buttons(self, parent):
        button_frame = tk.Frame(parent, bg='#ffffff', height=60)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        button_frame.pack_propagate(False)
        
        # Кнопки
        complete_btn = tk.Button(
            button_frame,
            text="✓ Выполнить",
            command=self.complete_task_gui,
            bg='#2196F3',
            fg='white',
            font=('Arial', 11),
            padx=15,
            cursor='hand2'
        )
        complete_btn.pack(side=tk.LEFT, padx=10)
        
        delete_btn = tk.Button(
            button_frame,
            text="🗑 Удалить",
            command=self.delete_task_gui,
            bg='#f44336',
            fg='white',
            font=('Arial', 11),
            padx=15,
            cursor='hand2'
        )
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Обновить",
            command=self.refresh_task_list,
            bg='#FF9800',
            fg='white',
            font=('Arial', 11),
            padx=15,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = tk.Button(
            button_frame,
            text="🚪 Выход",
            command=self.exit_app,
            bg='#607D8B',
            fg='white',
            font=('Arial', 11),
            padx=15,
            cursor='hand2'
        )
        exit_btn.pack(side=tk.RIGHT, padx=10)
        
    def load_tasks(self):
        tasks = []
        if os.path.exists(FILE_NAME):
            try:
                with open(FILE_NAME, "r", encoding="utf-8") as file:
                    for line in file:
                        if line.strip():
                            status, text, deadline = line.strip().split("|")
                            tasks.append({
                                "text": text,
                                "done": status == "1",
                                "deadline": deadline
                            })
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {e}")
        return tasks
    
    def save_tasks(self):
        try:
            with open(FILE_NAME, "w", encoding="utf-8") as file:
                for task in self.tasks:
                    status = "1" if task["done"] else "0"
                    file.write(f"{status}|{task['text']}|{task['deadline']}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def refresh_task_list(self, search_query=None):
        # Очищаем текущий список
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Фильтруем задачи если есть поиск
        tasks_to_show = self.tasks
        if search_query:
            search_query = search_query.lower()
            tasks_to_show = [task for task in self.tasks if search_query in task["text"].lower()]
        
        # Добавляем задачи в Treeview
        today = datetime.today().date()
        
        for i, task in enumerate(tasks_to_show, 1):
            deadline_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
            
            # Определяем статус
            if task["done"]:
                status = "✓ Выполнено"
                state = "Выполнено"
            else:
                status = "✗ Не выполнено"
                if deadline_date < today:
                    state = "⚠ ПРОСРОЧЕНО"
                else:
                    days_left = (deadline_date - today).days
                    if days_left == 0:
                        state = "Сегодня!"
                    elif days_left == 1:
                        state = f"Завтра ({days_left} день)"
                    elif days_left < 7:
                        state = f"Скоро ({days_left} дней)"
                    else:
                        state = f"до {task['deadline']}"
            
            # Цвет строки
            tags = ()
            if task["done"]:
                tags = ('done',)
            elif deadline_date < today:
                tags = ('overdue',)
            elif days_left <= 3:
                tags = ('urgent',)
            
            self.task_tree.insert(
                '',
                'end',
                text=str(i),
                values=(status, task["text"], task["deadline"], state),
                tags=tags
            )
        
        # Настройка тегов для цветов
        self.task_tree.tag_configure('done', foreground='gray')
        self.task_tree.tag_configure('overdue', foreground='red', font=('Arial', 10, 'bold'))
        self.task_tree.tag_configure('urgent', foreground='orange', font=('Arial', 10, 'bold'))
    
    def add_task_gui(self):
        text = self.task_text.get("1.0", tk.END).strip()
        deadline = self.date_entry.get()
        
        if not text:
            messagebox.showwarning("Предупреждение", "Введите описание задачи!")
            return
        
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты!")
            return
        
        self.tasks.append({
            "text": text,
            "done": False,
            "deadline": deadline
        })
        
        self.save_tasks()
        self.refresh_task_list()
        
        # Очищаем поля
        self.task_text.delete("1.0", tk.END)
        
        messagebox.showinfo("Успех", "Задача добавлена!")
    
    def complete_task_gui(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для отметки!")
            return
        
        item = selected[0]
        index = self.task_tree.index(item)
        
        # Если есть поиск, нужно найти реальный индекс
        if self.search_var.get():
            search_query = self.search_var.get().lower()
            visible_tasks = [task for task in self.tasks if search_query in task["text"].lower()]
            task_text = self.task_tree.item(item)['values'][1]
            # Находим задачу в основном списке
            for i, task in enumerate(self.tasks):
                if task["text"] == task_text:
                    self.tasks[i]["done"] = True
                    break
        else:
            if 0 <= index < len(self.tasks):
                self.tasks[index]["done"] = True
        
        self.save_tasks()
        self.refresh_task_list(self.search_var.get())
    
    def delete_task_gui(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления!")
            return
        
        item = selected[0]
        task_text = self.task_tree.item(item)['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить задачу:\n\n{task_text}\n\nВы уверены?"):
            # Находим и удаляем задачу из основного списка
            for i, task in enumerate(self.tasks):
                if task["text"] == task_text:
                    del self.tasks[i]
                    break
            
            self.save_tasks()
            self.refresh_task_list(self.search_var.get())
    
    def search_tasks_gui(self, event=None):
        query = self.search_var.get()
        self.refresh_task_list(query if query else None)
    
    def on_task_double_click(self, event):
        selected = self.task_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = self.task_tree.item(item)['values']
        
        # Показываем диалог редактирования
        self.edit_task_dialog(values[1])
    
    def edit_task_dialog(self, old_text):
        # Находим задачу
        task_index = -1
        for i, task in enumerate(self.tasks):
            if task["text"] == old_text:
                task_index = i
                break
        
        if task_index == -1:
            return
        
        task = self.tasks[task_index]
        
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать задачу")
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')
        dialog.resizable(False, False)
        
        # Центрируем окно
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Заголовок
        tk.Label(
            dialog,
            text="Редактирование задачи",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        ).pack(pady=20)
        
        # Поле для текста
        tk.Label(dialog, text="Описание задачи:", bg='#f0f0f0').pack(anchor='w', padx=40)
        text_editor = tk.Text(dialog, height=6, width=50, font=('Arial', 11))
        text_editor.pack(padx=40, pady=(5, 20))
        text_editor.insert("1.0", task["text"])
        
        # Поле для даты
        tk.Label(dialog, text="Дедлайн:", bg='#f0f0f0').pack(anchor='w', padx=40)
        date_frame = tk.Frame(dialog, bg='#f0f0f0')
        date_frame.pack(anchor='w', padx=40, pady=(5, 20))
        
        date_var = tk.StringVar(value=task["deadline"])
        date_entry = DateEntry(
            date_frame,
            textvariable=date_var,
            width=20,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Arial', 11)
        )
        date_entry.pack(side=tk.LEFT)
        
        # Чекбокс для статуса
        status_var = tk.BooleanVar(value=task["done"])
        status_check = tk.Checkbutton(
            dialog,
            text="Задача выполнена",
            variable=status_var,
            bg='#f0f0f0',
            font=('Arial', 11)
        )
        status_check.pack(anchor='w', padx=40, pady=(0, 20))
        
        # Кнопки
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        def save_changes():
            new_text = text_editor.get("1.0", tk.END).strip()
            if not new_text:
                messagebox.showwarning("Предупреждение", "Введите описание задачи!")
                return
            
            try:
                datetime.strptime(date_var.get(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return
            
            # Обновляем задачу
            self.tasks[task_index]["text"] = new_text
            self.tasks[task_index]["deadline"] = date_var.get()
            self.tasks[task_index]["done"] = status_var.get()
            
            self.save_tasks()
            self.refresh_task_list(self.search_var.get())
            dialog.destroy()
            messagebox.showinfo("Успех", "Задача обновлена!")
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Сохранить",
            command=save_changes,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Отмена",
            command=dialog.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 11),
            padx=20
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def exit_app(self):
        self.save_tasks()
        if messagebox.askyesno("Подтверждение", "Сохранить изменения и выйти?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()