
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pymysql

task_list = []
connection = pymysql.connect(user="root", password="toor", host="localhost", database="todo_list")
next_id = 1


# Not used
def save_list(bot, update):

    fh = open('task_list.txt', "w")
    for task in sorted(task_list):
        fh.write(task + "\n")
    bot.send_message(chat_id=update.message.chat_id, text="TODO list saved!")


def start(bot, update):
    global next_id
    load_query = "SELECT task FROM todo_list.todo"
    cursor = connection.cursor()
    cursor.execute(load_query)
    tasks = cursor.fetchall()

    task_list.clear()
    next_id += len(tasks)

    for task in tasks:
        task_list.append(task[0])
    bot.send_message(chat_id=update.message.chat_id, text="Welcome, TODO list loaded!")


def show_task(bot, update):
    if len(task_list) == 0:
        bot.send_message(chat_id=update.message.chat_id, text='Task list is empty!')
    for task in sorted(task_list):
        bot.send_message(chat_id=update.message.chat_id, text=task)


def new_task(bot, update, args):
    global next_id
    insert_query = "INSERT INTO todo_list.todo(id_task, task) VALUES (%s, %s)"
    cursor = connection.cursor()
    cursor.execute(insert_query, (next_id, args[0]))
    connection.commit()
    next_id += 1

    task_list.append(args[0])
    bot.send_message(chat_id=update.message.chat_id, text=args[0]+" added to the list!")


def remove_task(bot, update, args):
    remove_query = "DELETE FROM todo_list.todo WHERE task=%s"

    if args[0] in task_list:
        task_list.remove(args[0])
        cursor = connection.cursor()
        cursor.execute(remove_query, (args[0],))
        connection.commit()
        bot.send_message(chat_id=update.message.chat_id, text="Task removed!")
        # save_list(bot, update)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Task not found in the list!')


def remove_all_task(bot, update, args):
    remove_query = "DELETE FROM todo_list.todo WHERE task=%s"
    modified = False
    for task in task_list:
        if args[0] in task:
            task_list.remove(task)
            cursor = connection.cursor()
            cursor.execute(remove_query, (task,))
            cursor.close()
            modified = True
            bot.send_message(chat_id=update.message.chat_id, text=task+" Task removed!")
    if modified:
        connection.commit()
    else:
        bot.send_message(chat_id=update.message.chat_id, text="No task found to be removed!")


def help_on_message(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Im sorry i cant do that')


def main():
    updater = Updater("786366201:AAGfDQFB1zmLb--YCz9YxvRt1mO7wqHh1HM")
    dispatcher = updater.dispatcher
    handlers = []
    handlers.append(CommandHandler('start', start))
    handlers.append(CommandHandler('showTask', show_task))
    handlers.append(CommandHandler('newTask', new_task, pass_args=True))
    handlers.append(CommandHandler('removeTask', remove_task, pass_args=True))
    handlers.append(CommandHandler('removeAllTasks', remove_all_task, pass_args=True))
    handlers.append(MessageHandler(Filters.all, help_on_message))
    for handler in handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()

    updater.idle()
    connection.close()


if __name__ == "__main__":
    main()
