from tkinter import *
from tkinter.font import Font
from tetris_base import TetrisLogic


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

        for e in "<Up> <Left> <Right> <KeyPress-Down> <KeyRelease-Down>".split(
        ):
            self.tk.unbind_all(e)
        self.tk.bind("<Up>", self.logic.control_rotate)
        self.tk.bind("<Left>", self.logic.control_left)
        self.tk.bind("<Right>", self.logic.control_right)
        self.tk.bind("<KeyPress-Down>", self.speedUp)
        self.tk.bind("<KeyRelease-Down>", self.speedDown)

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
        self.btn_pause['text'] = '继续' if self.paused else '暂停'


TetrisGame()