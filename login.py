import tkinter as tk
import sqlite3
from functools import partial
import test

def login_window(root, rootmessage, id, num_oneday):
    root.withdraw()

    # 메인 창
    login_root = tk.Toplevel()
    login_root.title('로드 암기')
    login_root.state('zoomed')
    login_root.resizable(False, False)
    login_root.configure(bg = '#3C3A38')
    def close_all():
        login_root.destroy()
        root.destroy()
    login_root.protocol('WM_DELETE_WINDOW', close_all)

    # 중앙 배치를 위해 프레임 생성
    frame = tk.Frame(login_root)
    frame.config(bg = '#262421')
    frame.pack(expand = True)

    # 이미 모든 단어가 암기완료상태인지 확인
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) FROM MAIN WHERE ID = ?  AND word_status != "f"', (id, ))
    result = cur.fetchone()
    db.close()

    # 모든 단어가 암기완료상태면 더이상 할게 없다는 메시지 출력
    if result[0] == 0:
        # 설명라벨
        explain_label = tk.Label(frame)
        explain_label.config(text = '''
축하드립니다!

이 계정의 모든 과정을 완료하셨습니다.
아래 버튼을 통해 계정삭제를 진행해주세요.
                             ''', font = ('맑은 고딕', 24, 'bold'), fg = 'white')
        explain_label.config(bg = '#262421')
        explain_label.pack(padx =  50, pady = 40)

        # 계정 삭제 버튼
        delaccount_button = tk.Button(frame)
        delaccount_button.config(text = 'Delete this account', font = ('Arial', 20, 'bold'), fg = 'white')
        delaccount_button.config(bg = '#5d9948')
        def delete_id():
            # USER와 MAIN테이블에서 유저정보 삭제
            db = sqlite3.connect('data.db')
            cur = db.cursor()
            cur.execute('DELETE FROM USER WHERE ID = ?', (id,))
            cur.execute('DELETE FROM MAIN WHERE ID = ?', (id,))
            db.commit()
            db.close()

            # 메인 화면으로 돌아감
            login_root.destroy()
            root.deiconify()
            root.state('zoomed')
            rootmessage.config(text = 'Account deleted successfully.')
        delaccount_button.config(command = delete_id)
        delaccount_button.pack(pady = (0, 60))
    
    else:
        word_list = []
        mean_list = []

        # word_list와 mean_list에 단어들 가져오기 위해 데이터베이스 호출
        db = sqlite3.connect('data.db')
        cur = db.cursor()

        # word_status = 'r' 인 단어를 우선적으로 가져옴
        cur.execute('SELECT words, means FROM MAIN WHERE ID = ? AND word_status = "r"', (id, ))
        for word in cur.fetchall():
            word_list.append(word[0])
            mean_list.append(word[1])

        # word_status = '0'인 영어와 뜻을 number 순으로 num_oneday개 가져오기
        cur.execute('SELECT words, means FROM MAIN WHERE ID = ? AND word_status = "0" ORDER BY number ASC LIMIT ?', (id, num_oneday))
        for word in cur.fetchall():
            word_list.append(word[0])
            mean_list.append(word[1])

        db.close()

        # 위쪽 프레임
        up_frame = tk.Frame(frame)
        up_frame.config(bg = '#262421')
        up_frame.pack(expand = True)

        # 아래쪽 프레임
        down_frame = tk.Frame(frame)
        down_frame.config(bg = '#262421')
        down_frame.pack(expand = True)

        # 오늘의 단어 화면에 출력
        today_label = tk.Label(up_frame)
        today_label.config(text = f'오늘의 단어 ({len(word_list)}개)', font = ('맑은 고딕', 24, 'bold'), fg = 'white')
        today_label.config(bg = '#262421')
        today_label.grid(row = 0, column = 0, padx = (0, 30), pady = 30)

        # 숨기기 버튼
        hide_button = tk.Button(up_frame)
        hide_button.config(text = '뜻 숨기기', font = ('맑은 고딕', 12, 'bold'), fg = 'white')
        hide_button.config(bg = '#4d4c49')
        hide_button.grid(row = 0, column = 1)

        # 뜻 숨기기 보이기 기능을 위해 모든 뜻을 관리하는 리스트 생성
        mean_labels = []

        # 단어 리스트를 20씩 한 열에 배치하며 출력 (60개 초과될경우 출력이 이상하게되는데 그럴일 웬만해서 없음)
        for i in range(len(word_list)):
            row = i % 20
            col = (i // 20) * 2
            
            word_label = tk.Label(down_frame)
            word_label.config(text = word_list[i], font = ('Arial', 14), fg = 'white')
            word_label.config(bg = '#262421')
            word_label.grid(row = row, column = col, padx = (80, 20), sticky = 'w')
            mean_label = tk.Label(down_frame)
            mean_label.config(text = f': {mean_list[i]}', font = ('Arial', 14), fg = 'white')
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

        # 시험시작 버튼
        test_button = tk.Button(frame)
        test_button.config(text = 'Start test', font = ('Arial', 20, 'bold'), fg = 'white')
        test_button.config(bg = '#5d9948')
        def go_test():
            login_root.destroy()
            test.test_window(root, id, word_list, mean_list, num_oneday)
        test_button.config(command = go_test)
        test_button.pack(pady = (30, 10))

        # 안내문구
        explain_label = tk.Label(frame)
        explain_label.config(text = '시험을 시작하기 전에 오늘의 단어를 모두 외워주세요.', font = ('맑은 고딕', 12), fg = 'white')
        explain_label.config(bg = '#262421')
        explain_label.pack(padx = 20, pady = (0, 10))