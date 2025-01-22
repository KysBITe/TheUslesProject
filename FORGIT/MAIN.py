import curses
import json
import os
import time
import pyfiglet  # Импортируем библиотеку для генерации ASCII-арт

TASKS_FILE = "tasks.json"

LANGUAGES = {
    'en': {
        'kanban_manager': 'Kanban Manager',
        'planned': 'Planned',
        'in_progress': 'In Progress',
        'done': 'Done',
        'add_task': 'Add task',
        'move_task': 'Move task',
        'delete_task': 'Delete task',
        'exit': 'Exit',
        'enter_task_title': 'Enter task title: ',
        'enter_task_description': 'Enter task description: ',
        'enter_task_number': 'Enter task number to move (1 to {}): ',
        'enter_task_status': 'Enter new status (1. Planned, 2. In Progress, 3. Done): ',
        'task_not_found': 'Task not found.',
        'task_deleted': 'Task deleted successfully.',
        'enter_task_for_deletion': 'Enter task title to delete (or press "q" to quit): ',
        'task_list': 'Task list:',
    },
    'ru': {
        'kanban_manager': 'Канбан-менеджер',
        'planned': 'Запланировано',
        'in_progress': 'В процессе',
        'done': 'Готово',
        'add_task': 'Добавить задачу',
        'move_task': 'Переместить задачу',
        'delete_task': 'Удалить задачу',
        'exit': 'Выйти',
        'enter_task_title': 'Введите название задачи: ',
        'enter_task_description': 'Введите описание задачи: ',
        'enter_task_number': 'Введите номер задачи для перемещения (от 1 до {}): ',
        'enter_task_status': 'Введите новый статус (1. Запланировано, 2. В процессе, 3. Готово): ',
        'task_not_found': 'Задача не найдена.',
        'task_deleted': 'Задача удалена успешно.',
        'enter_task_for_deletion': 'Введите название задачи для удаления (или нажмите "q" для выхода): ',
        'task_list': 'Список задач:',
    }
}


# Структура задачи
class Task:
    def __init__(self, title, description, status="Запланировано"):
        self.title = title
        self.description = description
        self.status = status

    def to_dict(self):
        return {"title": self.title, "description": self.description, "status": self.status}

    @classmethod
    def from_dict(cls, data):
        return cls(data["title"], data["description"], data["status"])


# Сохранение задач в файл
def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump([task.to_dict() for task in tasks], file, ensure_ascii=False, indent=4)


# Загрузка задач из файла
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return [Task.from_dict(task) for task in json.load(file)]
    return []


# Вывод текста "HELLO" в стиле ASCII-арт по центру
def show_hello(stdscr, language):
    stdscr.clear()

    # Генерация ASCII-арта для текста "HELLO"
    ascii_art = pyfiglet.figlet_format("HELLO", font="slant")

    # Получаем размеры экрана
    max_height, max_width = stdscr.getmaxyx()

    # Разбиваем ASCII-арт на строки
    ascii_lines = ascii_art.splitlines()

    # Находим координаты для размещения в центре экрана
    start_y = max_height // 2 - len(ascii_lines) // 2
    start_x = max_width // 2 - len(ascii_lines[0]) // 2

    # Отображаем ASCII-арт в центре
    for i, line in enumerate(ascii_lines):
        stdscr.addstr(start_y + i, start_x, line)

    stdscr.refresh()
    time.sleep(3)  # Показываем "HELLO" 3 секунды


# Выбор языка
def choose_language(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Choose language:\n1. English\n2. Русский\n")
    choice = stdscr.getch()

    if choice == ord('1'):
        return 'en'
    elif choice == ord('2'):
        return 'ru'
    return 'en'  # Default to English


# Отображение задач в консоли
def display_tasks(stdscr, tasks, language):
    stdscr.clear()
    statuses = [LANGUAGES[language]['planned'], LANGUAGES[language]['in_progress'], LANGUAGES[language]['done']]
    max_height, max_width = stdscr.getmaxyx()

    # Заголовки
    stdscr.addstr(0, 0, LANGUAGES[language]['kanban_manager'], curses.A_BOLD)
    stdscr.addstr(2, 0, f"1. {LANGUAGES[language]['planned']}", curses.A_BOLD)
    stdscr.addstr(2, max_width // 3, f"2. {LANGUAGES[language]['in_progress']}", curses.A_BOLD)
    stdscr.addstr(2, 2 * max_width // 3, f"3. {LANGUAGES[language]['done']}", curses.A_BOLD)

    # Разделители
    stdscr.addstr(3, 0, "-" * max_width)

    # Вывод задач
    row = 4
    for status in statuses:
        stdscr.addstr(row, 0, f"{status}:", curses.A_BOLD)
        row += 1
        for task in tasks:
            if task.status == status:
                stdscr.addstr(row, 2, f"{task.title} - {task.description}")
                row += 1
        row += 1

    # Обновление экрана
    stdscr.refresh()


def add_task(stdscr, tasks, language):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, LANGUAGES[language]['enter_task_title'])
    title = stdscr.getstr(1, 0).decode("utf-8", errors="ignore")  # Используем "ignore", чтобы игнорировать ошибки декодирования

    stdscr.addstr(2, 0, LANGUAGES[language]['enter_task_description'])
    description = stdscr.getstr(3, 0).decode("utf-8", errors="ignore")  # Так же для описания

    tasks.append(Task(title, description, "Запланировано"))
    save_tasks(tasks)


# Перемещение задачи
def move_task(stdscr, tasks, language):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, LANGUAGES[language]['enter_task_number'].format(len(tasks)))
    task_index = int(stdscr.getstr(1, 0).decode("utf-8")) - 1

    if 0 <= task_index < len(tasks):
        task = tasks[task_index]
        stdscr.addstr(2, 0, f"Текущий статус задачи: {task.status}")
        stdscr.addstr(3, 0, LANGUAGES[language]['enter_task_status'])
        new_status = int(stdscr.getstr(4, 0).decode("utf-8"))

        if new_status == 1:
            task.status = LANGUAGES[language]['planned']
        elif new_status == 2:
            task.status = LANGUAGES[language]['in_progress']
        elif new_status == 3:
            task.status = LANGUAGES[language]['done']
        save_tasks(tasks)
    else:
        stdscr.addstr(5, 0, LANGUAGES[language]['task_not_found'])

    stdscr.refresh()
    stdscr.getch()


def del_task(stdscr, tasks, language):
    curses.echo()
    stdscr.clear()

    # Показываем список задач
    stdscr.addstr(0, 0, LANGUAGES[language]['task_list'])
    for i, task in enumerate(tasks):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {task.title} - {task.status}")

    stdscr.addstr(len(tasks) + 2, 0, LANGUAGES[language]['enter_task_for_deletion'])

    # Получаем ввод от пользователя без декодирования
    title = stdscr.getstr(len(tasks) + 3, 0).decode("utf-8", errors="ignore")  # Используем параметр "errors='ignore'"

    if title.lower() == 'q':
        return

    # Ищем задачу с таким названием
    task_to_delete = None
    for task in tasks:
        if task.title.lower() == title.lower():
            task_to_delete = task
            break

    if task_to_delete:
        tasks.remove(task_to_delete)
        save_tasks(tasks)
        stdscr.addstr(len(tasks) + 5, 0, LANGUAGES[language]['task_deleted'])
    else:
        stdscr.addstr(len(tasks) + 5, 0, LANGUAGES[language]['task_not_found'])

    stdscr.refresh()
    stdscr.getch()


# Основная функция
def main(stdscr):
    # Выбираем язык
    language = choose_language(stdscr)
    tasks = load_tasks()

    show_hello(stdscr, language)  # Показываем "HELLO" в ASCII-арте перед основным интерфейсом

    while True:
        display_tasks(stdscr, tasks, language)

        stdscr.addstr(20, 0, "Выберите опцию: ")
        stdscr.addstr(21, 0, f"1. {LANGUAGES[language]['add_task']}")
        stdscr.addstr(22, 0, f"2. {LANGUAGES[language]['move_task']}")
        stdscr.addstr(23, 0, f"3. {LANGUAGES[language]['delete_task']}")
        stdscr.addstr(24, 0, f"4. {LANGUAGES[language]['exit']}")

        choice = stdscr.getch()

        if choice == ord('1'):
            add_task(stdscr, tasks, language)
        elif choice == ord('2'):
            move_task(stdscr, tasks, language)
        elif choice == ord('3'):
            del_task(stdscr, tasks, language)
        elif choice == ord('4'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
