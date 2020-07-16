import telebot
import cv2
import sqlite3

baza = sqlite3.connect('bot.db')
sql = baza.cursor()
# 2 таблицы для связи "один-ко многим", т.к. один пользователь может иметь множество аудиосообщений
sql.execute("""CREATE TABLE IF NOT EXISTS users (id TEXT,name TEXT)""")
baza.commit()
sql.execute("""CREATE TABLE IF NOT EXISTS audio (link TEXT,id TEXT)""")
baza.commit()

# Существующие записи в базе данных
for value in sql.execute(f"SELECT * FROM audio"):
    print(value)



TOKEN = '1060649175:AAF7RHZRvRrUmkSocWKEG4VajvM5vqEaUF0'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text', 'photo', 'voice'])
def get_messages(message):
    print(message)
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Привет. Отправь мне фотографию")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Пока что я умею только обнаруживать на фотографии лица, подсчитывать их и отмечать."
                                               " Просто отправьте мне фотографию, а я проанализирую её и предоставлю вам результат")
    elif message.content_type == 'photo':
        print(message.photo[0].file_id)
        bot.send_message(message.from_user.id, "Я получил фото")

        file_info = bot.get_file(message.photo[-1].file_id)
        print(file_info)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('D:\PyProject\TeleBot\photo\photo.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
        image_path = 'D:\PyProject\TeleBot\photo\photo.jpg'
        face_cascade = cv2.CascadeClassifier('D:\PyInterpret\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(10, 10)
        )
        faces_detected = "Лиц обнаружено: " + format(len(faces))
        print(faces_detected)
        # Квадраты вокруг лиц
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

        cv2.imwrite("D:\PyProject\TeleBot\photo\photo.jpg", image)

        photo = open('D:\PyProject\TeleBot\photo\photo.jpg', 'rb')
        bot.send_photo(message.from_user.id, photo)
        #bot.send_photo(message.from_user.id, " FILEID ")
        bot.send_message(message.from_user.id, "Обнаружено лиц : " + format(len(faces)))

    elif message.content_type == 'voice':
        print('Received audio')
        bot.send_message(message.from_user.id, "Я получил аудиосообщение")

        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        id_user = 'id: '+ str(message.from_user.id)
        name_user = 'name: ' + str(message.from_user.first_name)
        path = r'D:\PyProject\TeleBot\audio\audio'+str(message.message_id)+'.ogg'
        print(path)
        with open(r'D:\PyProject\TeleBot\audio\audio'+str(message.message_id)+'.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        baza = sqlite3.connect('bot.db')
        sql = baza.cursor()
        sql.execute(f"SELECT id FROM users WHERE id = '{id_user}'")
        if sql.fetchone() is None:
            sql.execute(f"INSERT INTO users VALUES (?, ?)", (id_user, name_user))
            baza.commit()
        sql.execute(f"INSERT INTO audio VALUES (?, ?)", (path, id_user))
        baza.commit()
        bot.send_message(message.from_user.id, "Ваше аудиосообщение с номером "+str(message.message_id)+" сохранено в базу")


    else:
        bot.send_message(message.from_user.id, "Напишите /help.")



bot.polling(none_stop=True, interval=0)