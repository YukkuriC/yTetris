from tkinter import *
from tkinter.font import Font
from tetris_base import TetrisLogic

__doc__ = """ASCII俄罗斯方块
    基于tkinter模块实现的单人俄罗斯方块游戏  
    更新逻辑使用Tk.after事件实现  
    初步实现 "能玩儿" 目标
"""


class TetrisGame:
    def __init__(self, *a, **kw):
        # 参数
        self.paused = False
        self.updateStep = 800

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

        # 绑定游戏逻辑
        self.logic = TetrisLogic()
        self.logic.event_draw = self.draw

        self.tk.bind("<Up>", self.logic.control_rotate)
        self.tk.bind("<Left>", self.logic.control_left)
        self.tk.bind("<Right>", self.logic.control_right)
        self.tk.bind("<Down>", self.speedUp)
        self.tk.bind("<KeyRelease-Down>", self.speedDown)
        self.tk.bind("<w>", self.logic.control_rotate)
        self.tk.bind("<a>", self.logic.control_left)
        self.tk.bind("<d>", self.logic.control_right)
        self.tk.bind("<s>", self.speedUp)
        self.tk.bind("<KeyRelease-s>", self.speedDown)

        # 启动主循环
        self.draw()
        self.tk.mainloop()

    def draw(self):
        self.board['text'] = '\n'.join(self.logic.dump_lines())
        self.hud['text'] = self.logic.dump_info()

    def speedUp(self, *a):
        self.updateStep = 100

    def speedDown(self, *a):
        self.updateStep = 800

    def start_game(self):
        self.logic.reset()

        self.btn_start['state'] = DISABLED
        self.btn_pause['state'] = ACTIVE
        self.paused = True
        self.toggle_pause()
        self.run_game()

    def run_game(self):
        if not self.paused:
            self.logic.event_update()

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


TetrisGame()