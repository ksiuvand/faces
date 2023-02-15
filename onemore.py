import PIL
import dlib
import face_recognition
import cv2
import ast
import numpy as np
import os
import datetime
import mysql.connector


def connectDB():
    db = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd="",
      database="facesrec"

    )

    myCursor = db.cursor()
    # myCursor.execute('CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INTEGER(3), email VARCHAR(100), phone VARCHAR(100), visits INT, path VARCHAR(255), balls INT)')


# функция сравнение лиц по сетке (из бд и входящим)
def check_all_faces(image):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="facesrec"

    )

    myCursor = db.cursor()
    myCursor.execute("ALTER TABLE users MODIFY path TEXT")
    faces = face_recognition.face_locations(image)
    myCursor.execute("SELECT path FROM users")
    myresult = myCursor.fetchall()
    if len(myresult) >= 1:
        for img2 in myresult:
            # faces2 = face_recognition.face_locations(img2)
            if len(faces) > 0:
                img_encodings = face_recognition.face_encodings(image)[0]
                img2 = img2[0]
                img2 = img2.replace("   ", ",")
                img2 = img2.replace("  ", ",")
                img2 = img2.replace(" ", ",")
                res = ast.literal_eval(img2)
                # img2_encodings = face_recognition.face_encodings(res)[0]
                result = face_recognition.compare_faces([img_encodings], np.array(res))
                if result[0]:
                    return []
                else:
                    return img_encodings
            else:
                return []
    else:
        img_encodings = face_recognition.face_encodings(image)[0]
        return img_encodings


def found_all_faces(image_s):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="facesrec"

    )

    myCursor = db.cursor()
    img = image_s
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
    faces = faceCascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=3, minSize=(30, 30)
    )
    if len(faces) > 0:
        for i, (x, y, w, h) in enumerate(faces):
            face = img[y - 100:y + 30 + h, x - 30:x + 30 + w]
            image = face
            print(check_all_faces(face))
            if len(check_all_faces(face)) >= 1:
                sql = "INSERT INTO users (name, age, email, phone, visits, path, balls) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = ("name", 1, "email", 8922, 1, str(check_all_faces(face)), 1)
                myCursor.execute(sql, val)
                db.commit()

                print(f"face{i}.jpg is saved")


cap = cv2.VideoCapture(0)
i = 0
while True:
    ret, frame = cap.read()
    if i % 20 == 0:
        faces = face_recognition.face_locations(frame)
        if len(faces) >= 1:
            image = frame
            found_all_faces(image)
    i+=1

cap.release()
cv2.destroyAllWindows()