from tkinter import *
from tkinter.font import Font
from tetris_base import TetrisLogic

__doc__ = """ASCII俄罗斯方块-帧更新版
    相对于tetris_ascii.py增加实现了基于帧更新的实时游戏逻辑
    在加速下落事件上操作更流畅
"""


class TetrisLogicFrame(TetrisLogic):
    """ 按帧更新的俄罗斯方块逻辑 """
    NFRAME = 10
    NFRAME_SPEEDUP = 2

    def __init__(self, root, *a, **kw):
        super().__init__(*a, **kw)

        self.root = root  # 绑定
        self.is_speedup = False  # 是否处于加速模式
        self.frame_counter = 0  # 帧更新计数器

    def control_speedup(self, *a):
        """ 按下加速键 """
        if not self.is_speedup:  # 初次切换至加速模式时立即下落
            self.is_speedup = True
            self.frame_counter = 0

    def control_speeddown(self, *a):
        """ 松开加速键 """
        self.is_speedup = False

    def event_update_frame(self):
        """ 按帧更新游戏逻辑 """
        self.frame_counter -= 1
        if self.frame_counter <= 0:
            self.frame_counter = self.NFRAME
            if self.is_speedup:
                self.frame_counter = self.NFRAME_SPEEDUP
            self.event_update()

    def event_draw(self):
        """ 绑定游戏窗口的绘制事件 """
        self.root.draw()


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
        self.tk.bind("<KeyPress-s>", self.logic.control_speedup)
        self.tk.bind("<KeyRelease-s>", self.logic.control_speeddown)

        # 启动主循环
        self.tk.mainloop()

    def draw(self):
        lines = ['==' * (1 + self.logic.width)]
        if not self.logic.running:
            lines[0] = 'GAME  OVER'.center(2 + 2 * self.logic.width, '=')
        pool_tmp = [['[]' if x else '  ' for x in self.logic.pool[i]]
                    for i in range(self.logic.height)]
        if self.logic.curr_block:
            for pos in self.logic.curr_block:
                x = pos[0] + self.logic.curr_block.x
                y = pos[1] + self.logic.curr_block.y
                if y >= self.logic.height:
                    continue
                pool_tmp[y][x] = '<>'
        lines.extend(('|%s|' % (''.join(x))) for x in reversed(pool_tmp))
        lines.append(lines[0])
        self.board['text'] = '\n'.join(lines)

        # hud
        self.hud[
            'text'] = f'score:{self.logic.score} next:{"+".join(x.type for x in self.logic.next_block)}'
        if not self.logic.running:
            self.hud['text'] += ' Game Over'

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
        self.btn_pause['text'] = '继续' if self.paused else '暂停'
        if self.paused:  # 开始记录暂停事件
            self.pause_finished = False
        elif self.pause_finished:  # 重启游戏更新逻辑
            self.run_game()


TetrisGame()