import tkinter as tk
from tkinter import ttk
import mysql.connector

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")

        self.db_connection = mysql.connector.connect(
           host="localhost",
           user="root",
           password="12345",
           database="sql"
        )

        self.create_task_frame = ttk.Frame(self.root)
        self.create_task_frame.pack(pady=10)

        ttk.Label(self.create_task_frame, text="Новая задача:").grid(row=0, column=0, sticky=tk.W)
        self.task_entry = ttk.Entry(self.create_task_frame, width=40)
        self.task_entry.grid(row=0, column=1)
        ttk.Label(self.create_task_frame, text="Срок задачи:").grid(row=1, column=0, sticky=tk.W)
        self.deadline_entry = ttk.Entry(self.create_task_frame, width=40)
        self.deadline_entry.grid(row=1, column=1)
        ttk.Button(self.create_task_frame, text="Добавить задачу", command=self.add_task).grid(row=0, column=2,
                                                                                               rowspan=2)

        self.task_list_frame = ttk.Frame(self.root)
        self.task_list_frame.pack(padx=10, pady=10)

        ttk.Label(self.task_list_frame, text="Список задач:").grid(row=0, column=0, sticky=tk.W)
        self.task_tree = ttk.Treeview(self.task_list_frame, columns=("Task", "Deadline", "Completed"))
        self.task_tree.heading("#0", text="ID")
        self.task_tree.heading("Task", text="Задача")
        self.task_tree.heading("Deadline", text="Срок")
        self.task_tree.heading("Completed", text="Выполнено")
        self.task_tree.column("#0", width=50)
        self.task_tree.column("Task", width=300)
        self.task_tree.column("Deadline", width=150)
        self.task_tree.column("Completed", width=100)
        self.task_tree.grid(row=1, column=0, columnspan=4)

        self.create_table()

        ttk.Button(self.task_list_frame, text="Удалить задачу", command=self.delete_task).grid(row=2, column=0)
        ttk.Button(self.task_list_frame, text="Отметить как выполненную", command=self.mark_completed).grid(row=2,
                                                                                                            column=1)

        self.load_tasks()

    def create_table(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                              (id INT AUTO_INCREMENT PRIMARY KEY,
                              task TEXT NOT NULL,
                              deadline DATE,
                              completed BOOLEAN DEFAULT FALSE)''')
        except mysql.connector.Error as e:
            print("Ошибка при создании таблицы:", e)

    def load_tasks(self):
        self.task_tree.delete(*self.task_tree.get_children())
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM tasks")
            for row in cursor.fetchall():
                color = "green" if row[3] == 1 else "black"
                self.task_tree.insert("", "end", text=row[0], values=(row[1], row[2], "Да" if row[3] == 1 else "Нет"), tags=(color,))
        except mysql.connector.Error as e:
            print("Ошибка при загрузке задач:", e)

    def add_task(self):
        try:
            task = self.task_entry.get()
            deadline = self.deadline_entry.get()
            if task:
                cursor = self.db_connection.cursor()
                cursor.execute("INSERT INTO tasks (task, deadline) VALUES (%s, %s)", (task, deadline))
                self.db_connection.commit()
                self.task_entry.delete(0, tk.END)
                self.deadline_entry.delete(0, tk.END)
                self.load_tasks()
            else:
                print("Ошибка: пустая строка задачи")
        except mysql.connector.Error as e:
            print("Ошибка при добавлении задачи:", e)

    def delete_task(self):
        try:
            selected_item = self.task_tree.selection()
            if selected_item:
                task_id = self.task_tree.item(selected_item)["text"]
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
                self.db_connection.commit()
                self.task_tree.delete(selected_item)
        except mysql.connector.Error as e:
            print("Ошибка при удалении задачи:", e)

    def mark_completed(self):
        try:
            selected_item = self.task_tree.selection()
            if selected_item:
                task_id = self.task_tree.item(selected_item)["text"]
                cursor = self.db_connection.cursor()
                cursor.execute("UPDATE tasks SET completed=1 WHERE id=%s", (task_id,))
                self.db_connection.commit()
                self.load_tasks()
        except mysql.connector.Error as e:
            print("Ошибка при отметке задачи как выполненной:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()