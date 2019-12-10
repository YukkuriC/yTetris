from tkinter import *
from tkinter.font import Font
from tetris_base import TetrisLogicFrame

__doc__ = """ASCII俄罗斯方块-帧更新版
    相对于tetris_ascii.py增加实现了基于帧更新的实时游戏逻辑
    在加速下落事件上操作更流畅
"""


class TetrisGame:
    def __init__(self, *a, **kw):
        # 参数
        self.paused = False
        self.pause_finished = False  # 记录当前更新逻辑是否已中断，防止连点暂停导致多重更新
        self.updateStep = 75

        # 主窗口
        self.tk = Tk()
        self.tk.geometry('600x800')
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
        self.logic = TetrisLogicFrame(self)
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

        # 启动主循环
        self.draw()
        self.tk.mainloop()

    def draw(self):
        self.board['text'] = '\n'.join(self.logic.dump_lines())
        self.hud['text'] = self.logic.dump_info()

    def start_game(self):
        self.logic.reset()

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

        # 游戏继续，触发下一轮更新事件
        if self.logic.running:
            self.tk.after(self.updateStep, self.run_game)

        else:  # 游戏结束
            self.btn_start['state'] = ACTIVE
            self.btn_pause['state'] = DISABLED
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