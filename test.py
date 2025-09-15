import tkinter as tk
from tkinter import ttk
import sqlite3
from gtts import gTTS
import pygame
import threading
from io import BytesIO
from functools import partial
import random
from copy import deepcopy
import last

stage = 0
crtword = None
crtmean = []
correct_index = None
preword = None
premean = []
wrong_list = []

def core_logic(root, test_root, id, ui_elements, word_list, mean_list, entire_mean, num_oneday):
    global stage, crtword, crtmean, correct_index, preword, premean, wrong_list

    stage += 1

    # 시험이 종료되었을 경우
    if stage >= len(word_list):
        test_root.destroy()
        last.last_window(root, id, word_list, mean_list, wrong_list, num_oneday)
        # 시험이 끝났을때 프로그램을 종료하지 않고 다시 로그인해서 시도할경우를 위해 stage, wrong_list 초기화
        stage = 0
        wrong_list = []
    else:
        # 진행률 갱신
        ui_elements['progress_label'].config(text = f'{stage + 1} / {len(word_list)}')

        # ox_label 초기화
        for i in range(10):
            ui_elements['ox_labels'][i].config(text = ' ')

        # 현재단어, 뜻을 과거단어, 뜻으로 복사 후 출력
        preword = crtword
        ui_elements['preword_label'].config(text = preword)
        premean = deepcopy(crtmean)
        for i in range(10):
            ui_elements['pre_labels'][i].config(text = premean[i])

        answer = ui_elements['radio_value'].get()
        # 정답일 경우
        if answer == correct_index:
            ui_elements['answer_label'].config(text = '정답', fg = '#5d9948')
            ui_elements['ox_labels'][answer].config(text = 'o', fg = '#5d9948')
        # 오답일 경우
        else:
            ui_elements['answer_label'].config(text = '오답', fg = 'red')
            ui_elements['ox_labels'][answer].config(text = 'x', fg = 'red')
            ui_elements['ox_labels'][correct_index].config(text = 'o', fg = '#5d9948')
            # 틀린 단어 인덱스 모음 리스트 갱신
            wrong_list.append(stage - 1)

        # 현재단어, 뜻 수정
        crtword = word_list[stage]
        ui_elements['crtword_label'].config(text = crtword)
        while True:
            crtmean = random.sample(entire_mean, 9)
        
            if mean_list[stage] in crtmean:
                continue
            else:
                break
        correct_index = random.randint(0, 9)
        crtmean.insert(correct_index, mean_list[stage])
        for i in range(10):
            ui_elements['radiobuttons'][i].config(text = crtmean[i])

        # 페이지 넘어갈때마다 현재단어 자동재생
        tts = gTTS(text = crtword, lang = 'en')
        mp3_crt = BytesIO()
        tts.write_to_fp(mp3_crt)
        mp3_crt.seek(0)
        pygame.mixer.music.load(mp3_crt, "mp3")
        pygame.mixer.music.play()

def test_window(root, id, word_list, mean_list, num_oneday):
    # 테스트단어를 불러오기위해 데이터베이스 접근
    db = sqlite3.connect('data.db')
    cur = db.cursor()

    # word_status = '1' or '2' or '3' or '6' or '12'인 단어 가져와 word_list, mean_list에 추가
    cur.execute('''SELECT words, means FROM MAIN WHERE ID = ?
                AND (word_status = '1' OR word_status = '2' OR word_status = '3'
                OR word_status = '6' OR word_status = '12')
                ''', (id, ))
    for word in cur.fetchall():
        word_list.append(word[0])
        mean_list.append(word[1])
    # 모든 단어의 뜻을 entire_mean 리스트에 격납(객관식 문항을 만들기 위한 리스트)
    cur.execute("SELECT means FROM MAIN WHERE ID = ?", (id, ))
    entire_mean = [row[0] for row in cur.fetchall()]

    db.close()

    # 모든 단어가 word_status = 'f'는 아니지만 그날 시험봐야하는 단어가 없을 때
    if not word_list:
        last.last_window_none(root, id)
    # 정상적으로 테스트 진행
    else:
        # core_logic 호출 전 기본 세팅
        global crtword, crtmean, correct_index

        # word_list, mean_list 랜덤셔플
        combined = list(zip(word_list, mean_list))
        random.shuffle(combined)
        word_list, mean_list = zip(*combined)

        # word_list의 첫번째 단어를 crtword변수에 격납
        crtword = word_list[stage]

        # mean_list의 랜덤 9개(오답)를 현재뜻리스트에 격납
        while True:
            crtmean = random.sample(entire_mean, 9)
        
            # 정답이 포함되어있으면 다시
            if mean_list[stage] in crtmean:
                continue
            else:
                break

        # 정답을 집어넣을 인덱스
        correct_index = random.randint(0, 9)

        # crtmean리스트에 정답 집어넣음
        crtmean.insert(correct_index, mean_list[stage])

        # 소리재생라이브러리 pygame 초기화
        pygame.mixer.init()

        # 테스트화면 진입시 첫번째 단어 재생
        tts = gTTS(text = crtword, lang = 'en')
        mp3_crt = BytesIO()
        tts.write_to_fp(mp3_crt)
        mp3_crt.seek(0)
        pygame.mixer.music.load(mp3_crt, "mp3")
        pygame.mixer.music.play()

        # 메인 창
        test_root = tk.Toplevel(root)
        test_root.title('로드 암기')
        test_root.state('zoomed')
        test_root.resizable(False, False)
        test_root.configure(bg = '#3C3A38')
        def close_all():
            test_root.destroy()
            root.destroy()
        test_root.protocol('WM_DELETE_WINDOW', close_all)

        ui_elements = {}

        test_root.grid_rowconfigure(0, weight = 1)
        test_root.grid_columnconfigure(0, weight = 1)

        # 진행률 라벨
        ui_elements['progress_label'] = tk.Label(test_root, bg = '#3C3A38')
        ui_elements['progress_label'].config(text = f'{stage + 1} / {len(word_list)}')
        ui_elements['progress_label'].config(font = ('Arial', 20, 'bold'), fg = 'white')
        ui_elements['progress_label'].grid(row = 0, column = 0, columnspan = 4)

        # 이전 문제 프레임
        pre_frame = tk.Frame(test_root)
        pre_frame.config(width = 500, height = 600)
        pre_frame.config(bg = '#262421')
        pre_frame.grid(row = 1, column = 1, padx = (0, 100))
        pre_frame.grid_propagate(False)
        pre_frame.grid_columnconfigure(0, weight = 0)
        pre_frame.grid_columnconfigure(1, weight = 0)
        pre_frame.grid_columnconfigure(2, weight = 1)

        # 현재 문제 프레임
        crt_frame = tk.Frame(test_root)
        crt_frame.config(width = 500, height = 600)
        crt_frame.config(bg = '#262421')
        crt_frame.grid(row = 1, column = 2, padx = (100, 0))
        crt_frame.grid_propagate(False)
        crt_frame.grid_columnconfigure(0, weight = 1)

        test_root.grid_rowconfigure(2, weight = 1)
        test_root.grid_columnconfigure(3, weight = 1)
        
        # 현재 문제
        # 현재 문제 영단어
        ui_elements['crtword_label'] = tk.Label(crt_frame)
        ui_elements['crtword_label'].config(text = crtword, font = ('Arial', 24, 'bold'), fg = 'white')
        ui_elements['crtword_label'].config(bg = '#262421')
        ui_elements['crtword_label'].config(anchor = 'center')
        def readword_crt(event):
            # 단어 클릭 시 발음 읽기
            tts = gTTS(text = crtword, lang = 'en')
            mp3_crt = BytesIO()
            tts.write_to_fp(mp3_crt)
            mp3_crt.seek(0)
            pygame.mixer.music.load(mp3_crt, 'mp3')
            pygame.mixer.music.play()
        ui_elements['crtword_label'].bind('<Button-1>', lambda event: threading.Thread(target = readword_crt, args = (event, )).start())
        ui_elements['crtword_label'].grid(row = 0, column = 0, pady = 40)

        # 현재 문제 뜻
        style = ttk.Style()
        style.configure('Custom.TRadiobutton', background = '#262421', foreground = 'white', font = ('맑은 고딕', 16))
        radiobuttons = []
        ui_elements['radio_value'] = tk.IntVar()
        for i in range(10):
            radio_button = ttk.Radiobutton(crt_frame)
            radio_button.config(text = crtmean[i])
            radio_button.config(value = i)
            radio_button.config(variable = ui_elements['radio_value'])
            radio_button.config(style = 'Custom.TRadiobutton')
            radio_button.grid(row = i + 1, column = 0, padx = 50, sticky = "w")
            radiobuttons.append(radio_button)
        ui_elements['radiobuttons'] = radiobuttons

        # 다음 버튼
        next_button = tk.Button(crt_frame)
        next_button.config(text = 'Next', font = ('Arial', 18, 'bold'), fg = 'white')
        next_button.config(bg = '#5d9948')
        next_button.config(command = partial(core_logic, root, test_root, id, ui_elements, word_list, mean_list, entire_mean, num_oneday))
        next_button.grid(row = 11, pady = 30)

        # 이전 문제
        # 이전 문제 영단어
        ui_elements['preword_label'] = tk.Label(pre_frame)
        ui_elements['preword_label'].config(text = '', font = ('Arial', 24, 'bold'), fg = 'white')
        ui_elements['preword_label'].config(bg = '#262421')
        ui_elements['preword_label'].config(anchor = 'center')
        def readword_pre(event):
            # 단어 클릭 시 발음 읽기
            tts = gTTS(text = preword, lang = 'en')
            mp3_pre = BytesIO()
            tts.write_to_fp(mp3_pre)
            mp3_pre.seek(0)
            pygame.mixer.music.load(mp3_pre, 'mp3')
            pygame.mixer.music.play()
        ui_elements['preword_label'].bind('<Button-1>', lambda event: threading.Thread(target = readword_pre, args = (event, )).start())
        ui_elements['preword_label'].grid(columnspan = 10, pady = 40)

        # 이전 문제 뜻
        ox_labels = []
        pre_labels = []
        for i in range(10):
            ox_label = tk.Label(pre_frame)
            ox_label.config(text = ' ', font = ('맑은 고딕', 16), fg = 'white')
            ox_label.config(bg = '#262421')
            ox_label.grid(row = i + 1, column = 0, padx = (50, 5), sticky = 'w')
            ox_labels.append(ox_label)
            pre_label = tk.Label(pre_frame)
            pre_label.config(text = '', font = ('맑은 고딕', 16), fg = 'white')
            pre_label.config(bg = '#262421')
            pre_label.grid(row = i + 1, column = 1, sticky = 'w')
            pre_labels.append(pre_label)
        ui_elements['ox_labels'] = ox_labels
        ui_elements['pre_labels'] = pre_labels

        # 정답 오답 라벨
        ui_elements['answer_label'] = tk.Label(pre_frame)
        ui_elements['answer_label'].config(text = '', font = ('Arial', 18, 'bold'), fg = 'white')
        ui_elements['answer_label'].config(bg = '#262421')
        ui_elements['answer_label'].grid(row = 11, pady = 40, columnspan = 3)