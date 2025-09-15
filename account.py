import tkinter as tk
from tkinter import ttk
import sqlite3
from functools import partial

# word_options 변수에 단어 종류 격납
db = sqlite3.connect('data.db')
cur = db.cursor()
cur.execute('SELECT name FROM sqlite_master WHERE type="table";')
word_options = [table[0] for table in cur.fetchall() if table[0] not in ['USER', 'MAIN']]
db.close()

# 계정만들기 함수
def signup(signup_root, id_entry, word_combobox, rootmessage, errormessage):
    id = id_entry.get()
    word = word_combobox.get()
    
    # 아이디작성과 단어선택을 모두 하고 계정을 만들 경우
    if id and word and id != 'Username':
        try:
            db = sqlite3.connect('data.db')
            cur = db.cursor()

            # USER테이블과 MAIN테이블에 유저정보 등록
            cur.execute('INSERT INTO USER VALUES (?, ?)', (id, word))
            cur.execute(f'''
                        INSERT INTO MAIN (ID, number, words, means)
                        SELECT ?, {word}.number, {word}.words, {word}.means
                        FROM {word}
                        ''', (id, ))
            cur.execute('UPDATE MAIN SET word_status = "0" WHERE ID = ?', (id, ))

            db.commit()
            db.close()
            signup_root.destroy()
            rootmessage.config(text = 'Sign up successfully!')
            rootmessage.after(4000, lambda: rootmessage.config(text = ''))

        # 아이디가 이미 존재할 경우
        except sqlite3.IntegrityError:
            errormessage.config(text = 'The ID already exists.')
            errormessage.after(4000, lambda: errormessage.config(text = ''))

    # 아이디를 입력하지 않았거나 단어선택을 하지 않은 경우
    else:
        errormessage.config(text = 'Please enter both the ID and select a word.')
        errormessage.after(4000, lambda: errormessage.config(text = ''))

# 계정만들기
def signup_window(root, rootmessage, event):
    # 메인 창
    signup_root = tk.Toplevel(root)
    signup_root.resizable(False, False)
    signup_root.title('Sign up')
    signup_root.configure(bg = '#262421')
    win_width = 450
    win_height = 400
    x = int((root.winfo_screenwidth() / 2) - (win_width / 2))
    y = int((root.winfo_screenheight() / 2) - (win_height / 2))
    signup_root.geometry(f'{win_width}x{win_height}+{x}+{y}')

    # 중앙 배치를 위해 프레임 생성
    frame = tk.Frame(signup_root)
    frame.config(bg = '#262421')
    frame.pack(expand = True)

    # 설명라벨
    explain_label = tk.Label(frame)
    explain_label.config(text = 'Enter your ID', font = ('Arial', 24, 'bold'), fg = 'white')
    explain_label.config(bg = '#262421')
    explain_label.pack(pady = (0, 40))

    # ID 입력창
    id_entry = tk.Entry(frame)
    id_entry.config(bg = '#3C3A38', insertbackground = '#9E9D9C')
    id_entry.config(font = ('Arial', 20), fg = '#9E9D9C')
    id_entry.config(justify = 'center')
    id_entry.insert(0, 'Username')
    def clear(event):
        if id_entry.get() == 'Username':
            id_entry.delete(0, len(id_entry.get()))
    id_entry.bind('<Button-1>', clear)
    id_entry.pack(pady = (0, 40))

    # 단어선택 콤보박스
    word_combobox = ttk.Combobox(frame)
    word_combobox.config(values = word_options)
    word_combobox.config(font = ('Arial', 20))
    ttk.Style().theme_use('clam')
    word_combobox.config(state = 'readonly')
    word_combobox.config(width = 19)
    word_combobox.pack(pady = (0, 16))

    # 오류메시지
    errormessage = tk.Label(frame)
    errormessage.config(bg = '#262421')
    errormessage.config(text = '', font = ('Arial', 10), fg = 'red')
    errormessage.pack(pady = (0, 4))

    # 계정 만들기 버튼
    signup_button = tk.Button(frame)
    signup_button.config(text = 'Sign up', font = ('Arial', 20, 'bold'), fg = 'white')
    signup_button.config(bg = '#5d9948')
    signup_button.config(width = 17)
    signup_button.config(command = partial(signup, signup_root, id_entry, word_combobox, rootmessage, errormessage))
    signup_button.pack()

# 계정 삭제 함수
def delaccount(delaccount_root, id_entry, message, errormessage):
    id = id_entry.get()

    # 아이디창이 빈칸인 경우
    if id == '' or id == 'Username':
        errormessage.config(text = 'Please enter your ID')
        errormessage.after(4000, lambda: errormessage.config(text = ''))
    else:
        # USER테이블에 입력한 아이디가 존재하는지 확인 (idexist가 True면 아이디가 존재)
        db = sqlite3.connect('data.db')
        cur = db.cursor()
        cur.execute('SELECT * FROM USER WHERE ID = ?', (id, ))
        idexist = cur.fetchone() is not None
        db.close()

        if idexist:
            # 진짜 삭제할건지 확인메시지 창
            delaccount_sub = tk.Toplevel(delaccount_root)
            delaccount_sub.resizable(False, False)
            delaccount_sub.title('Delete account')
            delaccount_sub.configure(bg = '#262421')
            win_width = 450
            win_height = 300
            x = int((delaccount_root.winfo_screenwidth() / 2) - (win_width / 2))
            y = int((delaccount_root.winfo_screenheight() / 2) - (win_height / 2))
            delaccount_sub.geometry(f'{win_width}x{win_height}+{x}+{y}')

            # 중앙 배치를 위한 프레임 생성
            frame = tk.Frame(delaccount_sub)
            frame.config(bg = '#262421')
            frame.pack(expand = True)

            # 설명라벨
            explain1_label = tk.Label(frame)
            explain1_label.config(text = '정말로 이 계정을 삭제하시겠습니까?', font = ('맑은 고딕', 14, 'bold'), fg = 'white')
            explain1_label.config(bg = '#262421')
            explain1_label.pack(pady = (0, 10))
            explain2_label = tk.Label(frame)
            explain2_label.config(text = f'" {id} "', font = ('Arial', 14, 'bold'), fg = '#5d9948')
            explain2_label.config(bg = '#262421')
            explain2_label.pack(pady = (0 , 10))
            explain3_label = tk.Label(frame)
            explain3_label.config(text = '계정삭제를 하면 이 계정의 모든 과정은\n영구적으로 삭제됩니다.', font = ('맑은 고딕', 14, 'bold'), fg = 'white')
            explain3_label.config(bg = '#262421')
            explain3_label.pack(pady = (0, 30))

            # 삭제, 취소 버튼
            button_frame = tk.Frame(frame)
            button_frame.config(bg = '#262421')
            button_frame.pack()

            delete_button = tk.Button(button_frame)
            delete_button.config(text = 'Delete', font = ('Arial', 14), fg = 'black')
            delete_button.config(bg = 'white')
            def delete_id(id, event = None):
                # USER테이블과 MAIN테이블에서 유저정보 삭제
                db = sqlite3.connect('data.db')
                cur = db.cursor()
                cur.execute('DELETE FROM USER WHERE ID = ?', (id,))
                cur.execute('DELETE FROM MAIN WHERE ID = ?', (id,))
                db.commit()
                db.close()

                delaccount_root.destroy()
                message.config(text = 'Account deleted successfully.')
                message.after(4000, lambda: message.config(text = ''))
            delete_button.bind('<Button-1>', partial(delete_id, id))
            delete_button.grid(row = 0, column = 0, padx = (0, 40))

            # 취소 버튼
            cancel_button = tk.Button(button_frame)
            cancel_button.config(text = 'Cancel')
            cancel_button.config(bg = 'white')
            cancel_button.config(font = ('Arial', 14), fg = 'black')
            def delete_cancel(delaccount_sub, event = None):
                delaccount_sub.destroy()
            cancel_button.bind('<Button-1>', partial(delete_cancel, delaccount_sub))
            cancel_button.grid(row = 0, column = 1, padx = (40, 0))
        else:
            errormessage.config(text = 'ID not found')
            errormessage.after(4000, lambda: errormessage.config(text = ''))

# 계정 삭제
def delaccount_window(root, rootmessage, event):
    # 메인 창
    delaccount_root = tk.Toplevel(root)
    delaccount_root.resizable(False, False)
    delaccount_root.title('Delete account')
    delaccount_root.configure(bg = '#262421')
    win_width = 450
    win_height = 300
    x = int((root.winfo_screenwidth() / 2) - (win_width / 2))
    y = int((root.winfo_screenheight() / 2) - (win_height / 2))
    delaccount_root.geometry(f'{win_width}x{win_height}+{x}+{y}')

    # 중앙 배치를 위해 프레임 생성
    frame = tk.Frame(delaccount_root)
    frame.config(bg = '#262421')
    frame.pack(expand = True)

    # 설명라벨
    explain_label = tk.Label(frame)
    explain_label.config(text = 'Enter the ID to delete', font = ('Arial', 24, 'bold'), fg = 'white')
    explain_label.config(bg = '#262421')
    explain_label.pack(pady = (0, 40))

    # ID 입력창
    id_entry = tk.Entry(frame)
    id_entry.config(bg = '#3C3A38', insertbackground = '#9E9D9C')
    id_entry.config(font = ('Arial', 20), fg = '#9E9D9C')
    id_entry.config(justify = 'center')
    id_entry.insert(0, 'Username')
    def clear(event):
        if id_entry.get() == 'Username':
            id_entry.delete(0, len(id_entry.get()))
    id_entry.bind('<Button-1>', clear)
    id_entry.pack(pady = (0, 22))

    # 오류 메시지
    errormessage = tk.Label(frame)
    errormessage.config(text = '', font = ('Arial', 10), fg = 'red')
    errormessage.config(bg = '#262421')
    errormessage.config()
    errormessage.pack(pady = (0, 4))

    # 계정 삭제 버튼
    delaccount_button = tk.Button(frame)
    delaccount_button.config(text = 'Delete account', font = ('Arial', 20), fg = 'black')
    delaccount_button.config(bg = '#dad8d6')
    delaccount_button.config(width = 17)
    delaccount_button.config(command = partial(delaccount, delaccount_root, id_entry, rootmessage, errormessage))
    delaccount_button.pack()