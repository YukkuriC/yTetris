from tkinter import *
from tkinter.font import Font
from tetris_base import TetrisLogicVersus, TetrisLogicAuto
from tetris_ai_examples import RandomDumb

__doc__ = """ASCII俄罗斯方块-人机对战版
    在tetris_ascii_versus.py基础上实现了人机对战、AI接口功能
"""


class TetrisGame:
    def __init__(self, *a, **kw):
        # 参数
        self.paused = False
        self.pause_finished = False  # 记录当前更新逻辑是否已中断，防止连点暂停导致多重更新
        self.updateStep = 75

        # 主窗口
        self.tk = Tk()
        self.tk.geometry('700x800')
        # self.tk.resizable(0, 0)

        # 控制区
        frame = Frame(self.tk)
        frame.pack(fill=X)
        self.btn_start = Button(frame, text='开始', command=self.start_game)
        self.btn_start.grid(row=0, column=0)
        self.btn_pause = Button(
            frame, text='暂停', command=self.toggle_pause, state=DISABLED)
        self.btn_pause.grid(row=0, column=1)
        self.hud = Label(frame)
        self.hud.grid(row=0, column=2)

        # 游戏显示区
        self.board = Label(
            self.tk, font=Font(family='Consolas', size=20), justify=LEFT)
        self.board.pack(fill=X, anchor=W)

        # 绑定游戏操作 玩家1
        self.logic = TetrisLogicVersus(self)
        self.tk.bind("<w>", self.logic.control_rotate)
        self.tk.bind("<a>", self.logic.control_left)
        self.tk.bind("<d>", self.logic.control_right)
        self.tk.bind("<s>", self.logic.control_speedup)
        self.tk.bind("<KeyRelease-s>", self.logic.control_speeddown)
        self.tk.bind("<Up>", self.logic.control_rotate)
        self.tk.bind("<Left>", self.logic.control_left)
        self.tk.bind("<Right>", self.logic.control_right)
        self.tk.bind("<Down>", self.logic.control_speedup)
        self.tk.bind("<KeyRelease-Down>", self.logic.control_speeddown)

        # 绑定游戏操作 玩家2(AI)
        self.logic2 = TetrisLogicAuto(RandomDumb(), self)

        # 玩家间绑定对手
        self.logic.opponent = self.logic2
        self.logic2.opponent = self.logic

        # 启动主循环
        self.draw()
        self.tk.mainloop()

    def draw(self):
        board1, board2 = self.logic.dump_lines(), self.logic2.dump_lines()
        self.board['text'] = '\n'.join(
            (x[:-1] + y for x, y in zip(board1, board2)))

        # hud
        self.hud[
            'text'] = f'{self.logic.dump_info()} || {self.logic2.dump_info()}'

    def start_game(self):
        self.logic.reset()
        self.logic2.reset()

        self.btn_start['state'] = DISABLED
        self.btn_pause['state'] = ACTIVE
        self.paused = True
        self.toggle_pause()

        self.run_game()

    def run_game(self):
        if self.paused:
            self.pause_finished = True
            return

        # 更新帧
        self.logic.event_update_frame()
        self.logic2.event_update_frame()

        # 游戏继续，触发下一轮更新事件
        if self.logic.running and self.logic2.running:
            self.tk.after(self.updateStep, self.run_game)

        else:  # 游戏结束
            self.btn_start['state'] = ACTIVE
            self.btn_pause['state'] = DISABLED
            self.logic.paused = self.logic2.paused = True
            self.draw()

    def toggle_pause(self, *a):
        self.paused = not self.paused
        self.logic.paused = self.paused
        self.btn_pause['text'] = '继续' if self.paused else '暂停'
        if self.paused:  # 开始记录暂停事件
            self.pause_finished = False
        elif self.pause_finished:  # 重启游戏更新逻辑
            self.run_game()


TetrisGame()