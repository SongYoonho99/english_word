import tkinter as tk
import sqlite3
from functools import partial

def last_window(root, id, word_list, mean_list, wrong_list, num_oneday):
    # 테스트종료 데이터베이스 조작
    db = sqlite3.connect('data.db')
    cur = db.cursor()

    # word_status = 'r'인것들 '1'로 변경
    cur.execute('UPDATE MAIN SET word_status = "1" WHERE ID = ? AND word_status = "r"', (id, ))

    # word_status = '12'인 것들중 시험봐서 틀린거 word_status = 'r'로 변경
    wrongword_list = [word_list[i] for i in wrong_list]
    query = f'''
    UPDATE MAIN
    SET word_status = "r"
    WHERE ID = ? 
    AND word_status = "12" 
    AND words IN ({','.join(['?'] * len(wrongword_list))})
    '''
    cur.execute(query, (id, *wrongword_list))

    # word_status = '12'인 것들중 시험봐서 맞은거 word_status = 'f'로 변경
    cur.execute('UPDATE MAIN SET word_status = "f" WHERE ID = ? AND word_status = "12"', (id, ))

    # word_status = 'n'(1 <= n <= 11)인것들 word_status = 'n + 1'로 변경
    for i in range(11, 0, -1):
        cur.execute('UPDATE MAIN SET word_status = ? WHERE ID = ? AND word_status = ?', (str(i + 1), id, str(i)))

    # word_status = '0' 것들중 number 순으로 num_oneday개의 행을 word_status = '1'로 변경
    query = '''
    UPDATE MAIN 
    SET word_status = '1'
    WHERE rowid IN (
        SELECT rowid FROM MAIN 
        WHERE ID = ? AND word_status = '0'
        ORDER BY number ASC
        LIMIT ?)
    '''
    cur.execute(query, (id, num_oneday))

    db.commit()
    db.close()

    last_root = tk.Toplevel(root)
    last_root.title('로드 암기')
    last_root.state('zoomed')
    last_root.resizable(False, False)
    last_root.configure(bg = '#3C3A38')
    def close_all():
        last_root.destroy()
        root.destroy()
    last_root.protocol('WM_DELETE_WINDOW', close_all)

    # 중앙 배치를 위해 프레임 생성
    frame = tk.Frame(last_root)
    frame.config(bg = '#262421')
    frame.pack(expand = True)

    # 위쪽 프레임
    up_frame = tk.Frame(frame)
    up_frame.config(bg = '#262421')
    up_frame.pack(expand = True)

    # 아래쪽 프레임
    down_frame = tk.Frame(frame)
    down_frame.config(bg = '#262421')
    down_frame.pack(expand = True)

    # 틀린 단어 라벨
    wrongword_label = tk.Label(up_frame)
    wrongword_label.config(text = f'틀린 단어 ({len(wrong_list)}개)', font = ('맑은 고딕', 24, 'bold'), fg = 'white')
    wrongword_label.config(bg = '#262421')
    wrongword_label.grid(row = 0, column = 0, padx = (0, 30), pady = 30)

    # 숨기기 버튼
    hide_button = tk.Button(up_frame)
    hide_button.config(text = '뜻 숨기기', font = ('맑은 고딕', 12, 'bold'), fg = 'white')
    hide_button.config(bg = '#4d4c49')
    hide_button.grid(row = 0, column = 1)

    # 뜻 숨기기 보이기 기능을 위해 모든 뜻을 관리하는 리스트 생성
    mean_labels = []

    # 단어 리스트를 출력 (20개씩 한 열에 배치)
    for i in range(len(wrong_list)):
        row = i % 20
        col = (i // 20) * 2

        word_label = tk.Label(down_frame)
        word_label.config(text = word_list[wrong_list[i]], font = ('Arial', 14), fg = 'white')
        word_label.config(bg = '#262421')
        word_label.grid(row = row, column = col, padx = (80, 20), sticky = 'w')
        mean_label = tk.Label(down_frame)
        mean_label.config(text = f': {mean_list[wrong_list[i]]}', font = ('Arial', 14), fg = 'white')
        mean_label.config(bg = '#262421')
        mean_label.grid(row = row, column = col + 1, padx = (0, 80), sticky = 'w')
        mean_labels.append(mean_label)
    
    # 뜻 숨기기 보이기 옵션
    option = True
    def hide():
        nonlocal option
        if option:
            hide_button.config(text = '뜻 보이기')
            for label in mean_labels:
                label.config(fg = '#262421')
            option = False
        else:
            hide_button.config(text = '뜻 숨기기')
            for label in mean_labels:
                label.config(fg = 'white')
            option = True       
    hide_button.config(command = hide) 

    # 시험종료 버튼
    finish_button = tk.Button(frame)
    finish_button.config(text = 'Finish test', font = ('Arial', 20, 'bold'), fg = 'white')
    finish_button.config(bg = '#5d9948')
    def finish():
        last_root.destroy()
        root.state('zoomed')
        root.deiconify()
    finish_button.config(command = finish)
    finish_button.pack(pady = (30, 10))

    # 안내문구
    ex = tk.Label(frame)
    ex.config(text = '시험을 종료하기 전에 틀린 단어를 모두 외워주세요.', font = ('맑은 고딕', 12), fg = 'white')
    ex.config(bg = '#262421')
    ex.pack(padx = 20, pady = (0, 10))

# 모든 단어가 word_status = 'f'는 아니지만 그날 시험봐야하는 단어가 없을 때
def last_window_none(root, id):
    # 테스트종료 데이터베이스 조작
    db = sqlite3.connect('data.db')
    cur = db.cursor()

    # word_status = 4, 5, 7, 8, 9, 10, 11인것들 word_status += 1로 변경
    for i in [11, 10, 9, 8, 7, 5, 4]:
        cur.execute('UPDATE MAIN SET word_status = ? WHERE ID = ? AND word_status = ?', (str(i + 1), id, str(i)))

    db.commit()
    db.close()

    last_root = tk.Toplevel(root)
    last_root.title('로드 암기')
    last_root.state('zoomed')
    last_root.resizable(False, False)
    last_root.configure(bg = '#3C3A38')
    def close_all():
        last_root.destroy()
        root.destroy()
    last_root.protocol('WM_DELETE_WINDOW', close_all)

    # 중앙 배치를 위해 프레임 생성
    frame = tk.Frame(last_root)
    frame.config(bg = '#262421')
    frame.pack(expand = True)

    # 설명라벨
    explain_label = tk.Label(frame)
    explain_label.config(text = '''
오늘은 테스트 해야 할 단어가 없습니다.
아직 이 계정의 모든 과정이 끝난것은 아니므로
다음 수업때 다시 로그인 해주세요.
    ''', font = ('맑은 고딕', 24, 'bold'), fg = 'white')
    explain_label.config(bg = '#262421')
    explain_label.pack(padx =  50, pady = 40)

    # 시험종료 버튼
    finish_button = tk.Button(frame)
    finish_button.config(text = 'Finish test', font = ('Arial', 20, 'bold'), fg = 'white')
    finish_button.config(bg = '#5d9948')
    def finish():
        last_root.destroy()
        root.state('zoomed')
        root.deiconify()
    finish_button.config(command = finish)
    finish_button.pack(pady = (0, 40))