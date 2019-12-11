from tetris_base import TetrisAI
import random


class RandomDumb(TetrisAI):
    """ 随机操作AI，用于演示各操作符功能 """

    def __init__(self, width, height):
        self.is_speedup = False

    def evaluate(self, *a, **kw):
        """ 无视参数输入返回随机动作 """
        res = ''
        if random.randrange(2):  # 左右随机
            res += random.choice('ad')
        if random.randrange(2):  # 旋转随机
            res += 'w'
        if random.randrange(2):  # 加速随机
            self.is_speedup = not self.is_speedup
            res += 'ns' [self.is_speedup]
        return res