import os
import sys
import tkinter as tk
from tkinter import PhotoImage
import sqlite3
from functools import partial
import account
import login

# 하루에 추가하는 단어 수 (반드시 10 이상으로 할것. 권장 : 12 ~ 20)
num_oneday = 20

# data.db, MAIN, USER가 없을경우 자동으로 생성
db = sqlite3.connect("data.db")
cur = db.cursor()

query1 = '''
CREATE TABLE IF NOT EXISTS USER (
    ID text PRIMARY KEY,
    what_word text
)
'''
query2 = '''
CREATE TABLE IF NOT EXISTS MAIN (
    ID text,
    number int,
    words text,
    means text,
    word_status char(1)
)
'''

cur.execute(query1)
cur.execute(query2)
db.commit()
db.close()

# 메인 창
root = tk.Tk()
root.title('로드 암기')
root.geometry('800x700')
root.state('zoomed')
root.configure(bg = '#3C3A38')
root.option_add('*Font', '맑은고딕 16')

# road.png 실행파일에 넣기 위해
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 메인로고
image_path = resource_path('road.png')
image = PhotoImage(file=image_path)
mainlogo_label = tk.Label(root)
mainlogo_label.config(image = image, bd = 0)
mainlogo_label.pack(pady = (60, 0))

# 중앙 배치를 위한 프레임 생성
frame = tk.Frame(root)
frame.config(bg = '#262421')
frame.pack(expand = True)

# ID 입력창
login_entry = tk.Entry(frame)
login_entry.config(bg = '#3C3A38', insertbackground = '#9E9D9C')
login_entry.config(font = ('Arial', 20), fg = '#9E9D9C')
login_entry.config(justify = 'center')
login_entry.insert(0, 'Username')
def clear(event):
    if login_entry.get() == 'Username':
        login_entry.delete(0, len(login_entry.get()))
login_entry.bind('<Button-1>', clear)
login_entry.pack(padx = 60, pady = (60, 50))

# 메시지 라벨(로그인버튼을 눌렀을때 호출할 함수에 매개변수로 전달하기 위해 미리 선언)
rootmessage = tk.Label(frame)

# 로그인 버튼
login_button = tk.Button(frame)
login_button.config(text = 'Log in', font = ('Arial', 20, 'bold'), fg = 'white')
login_button.config(bg = '#5d9948')
login_button.config(width = 17)
def login_check(root, login_entry):
    id = login_entry.get()

    # 로그인 시도시 USER테아블에 아이디의 존재여부 확인
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('SELECT * FROM USER WHERE ID = ?', (id, ))
    idexist = cur.fetchone() is not None
    db.close()

    if idexist:
        # 정상적으로 로그인 될 경우 login.py의 login_window 함수 실행
        login_entry.delete(0, len(login_entry.get()))
        login_entry.insert(0, 'Username')
        login.login_window(root, rootmessage, id, num_oneday)
    else:
        rootmessage.config(text = 'ID not found')
        rootmessage.config(fg = 'red')
        rootmessage.after(4000, lambda: rootmessage.config(text = '', fg = 'white'))

login_button.config(command = partial(login_check, root, login_entry))
login_button.pack(pady = (0, 4))

# Enter 키로도 로그인 가능
def login_enter(event, root, login_entry):
    login_check(root, login_entry)
root.bind('<Return>', lambda event: login_enter(event, root, login_entry))

# 메시지 라벨
rootmessage.config(text = '', font = ('Arial', 10), fg = 'white')
rootmessage.config(bg = '#262421')
rootmessage.pack(pady = (0, 20))

# or 라벨
or_label = tk.Label(frame)
or_label.config(text = 'OR', font = ('Arial', 14, 'bold'), fg = 'white')
or_label.config(bg = '#262421')
or_label.pack(pady = (0, 40))

# 계정 등록, 계정 탈퇴 라벨
account_frame = tk.Frame(frame)
account_frame.config(bg = '#262421')
account_frame.pack(pady = (0, 40))

signup_label = tk.Label(account_frame)
signup_label.config(text = 'Sign up', font = ('Arial', 12), fg = 'white')
signup_label.config(bg = '#262421')
signup_label.bind('<Button-1>', partial(account.signup_window, root, rootmessage))
signup_label.grid(row = 0, column = 0, padx = (0, 30))

delaccount_label = tk.Label(account_frame)
delaccount_label.config(text = 'Delete account', font = ('Arial', 12), fg = 'white')
delaccount_label.config(bg = '#262421')
delaccount_label.bind('<Button-1>', partial(account.delaccount_window, root, rootmessage))
delaccount_label.grid(row = 0, column = 1, padx = (30, 0))

account_frame.grid_columnconfigure(0, weight=1, uniform = 'col')
account_frame.grid_columnconfigure(1, weight=1, uniform = 'col')

root.mainloop()