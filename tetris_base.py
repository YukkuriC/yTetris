import random, time


class RandSeq:
    """
    确定随机序列生成器
    """
    BATCH = 100
    SEED = time.time()

    def __init__(self, func, seed=None):
        self.pool = []
        self.seed = self.SEED if seed is None else seed
        self.func = func
        self.gen_rand()

    def gen_rand(self):
        """ 一次性生成下一轮随机序列与新的种子 """
        random.seed(self.seed)
        self.seed = random.random()
        for i in range(self.BATCH):
            self.pool.append(self.func())

    def pop(self):
        """ 获取下一个随机值 """
        if not self.pool:
            self.gen_rand()
        return self.pool.pop()


class Block:
    """
    方块类
    """

    BLOCK_NAMES = 'JLTIZSO'
    BLOCKS = [
        ((-1, 0), (1, 0), (-1, 1)),  # J
        ((-1, 0), (1, 0), (1, 1)),  # L
        ((-1, 0), (1, 0), (0, 1)),  # T
        ((-1, 0), (1, 0), (2, 0)),  # I
        ((0, 1), (1, 0), (-1, 1)),  # Z
        ((0, 1), (-1, 0), (1, 1)),  # S
        ((0, 1), (1, 0), (1, 1)),  # O
    ]

    @classmethod
    def get(cls):
        """ 随机获取方块 """
        return cls(random.randrange(7))

    def __init__(self, type):
        self.type = self.BLOCK_NAMES[type]  # 块类型
        self.outers = self.BLOCKS[type]  # 中心块以外
        self.x = self.y = 0
        self.phase = 0  # 旋转相位

    def rotate(self, back=False):
        if self.type == 'O':  # 2*2不旋转
            return
        if self.type in 'IZS' and (self.phase ^ back):  # 中心对称方块
            back = not back

        if back:  # 正旋转
            self.phase += 1
            self.outers = tuple((y, -x) for x, y in self.outers)
        else:  # 反旋转
            self.phase -= 1
            self.outers = tuple((-y, x) for x, y in self.outers)

        self.phase %= 4

    def __iter__(self):
        """ 迭代获取所有块相对中心位置偏移 """
        yield (0, 0)
        yield from self.outers


class TetrisLogic:
    """
    游戏逻辑类
    try_*: 尝试移动方块
    control_*: 游戏玩家操作
    event_*: 游戏事件
    """

    def __init__(self, size=(10, 20), seed=None):
        self.width, self.height = size  # 场地宽高（格）
        self.seed = seed  # 随机种子
        self.reset()

    def reset(self):
        """ 开局 """
        self.running = True  # 玩家尚未死亡
        self.pool = [[0] * self.width
                     for _ in range(self.height + 1)]  # 游戏场地，顶行用于判断死亡
        self.curr_block = None  # 当前方块
        self.block_settled = False  # 游戏逻辑中下回合放置当前控制方块
        self.score = 0

        # 生成方块序列
        self.block_seq = RandSeq(Block.get, self.seed)
        self.next_block = [self.block_seq.pop(), self.block_seq.pop()]

    def try_move(self, new_pos):
        """ 判断方块下个位置是否可移动 """
        if not self.curr_block:
            return False

        # 判断场地相交
        try:
            for offset in self.curr_block:
                nx, ny = tuple(a + b for a, b in zip(offset, new_pos))
                assert 0 <= nx < self.width and 0 <= ny  # 左右底边
                if ny > self.height:  # 无上界
                    continue
                if self.pool[ny][nx]:
                    return False
        except (IndexError, AssertionError):
            return False

        # 移动方块
        self.curr_block.x, self.curr_block.y = new_pos
        return True

    def try_rotate(self, back=False):
        """ 判断当前位置是否可旋转 """
        if not self.curr_block:
            return False
        self.curr_block.rotate(back)
        # 旋转后防止重叠
        for dy in range(3):
            curr_y = self.curr_block.y + dy
            if curr_y >= self.height:  # 场外不可旋转
                break
            for dx in 0, 1, -1:
                if self.try_move((self.curr_block.x + dx, curr_y)):
                    return True

        # 附近无可用空隙，旋转复原
        self.curr_block.rotate(not back)
        return False

    def control_left(self, *a):
        if not self.curr_block:
            return
        if self.try_move((self.curr_block.x - 1, self.curr_block.y)):
            self.block_settled = False
            self.event_draw()

    def control_right(self, *a):
        if not self.curr_block:
            return
        if self.try_move((self.curr_block.x + 1, self.curr_block.y)):
            self.block_settled = False
            self.event_draw()

    def control_rotate(self, *a):
        if not self.curr_block:
            return
        if self.try_rotate():
            self.block_settled = False
            self.event_draw()

    def control_swap(self, *a):
        self.next_block = self.next_block[::-1]
        self.event_draw()

    def event_draw(self, *a):
        """ 绘图事件 """
        pass

    def event_clear(self, nline):
        """ 行消除 """
        self.score += nline * nline

    def event_update(self):
        """ 游戏逻辑更新 """
        if not self.running:
            return

        # 方块逻辑
        if self.curr_block:
            if self.block_settled:  # 本回合放置方块
                for pos in self.curr_block:
                    x = pos[0] + self.curr_block.x
                    y = pos[1] + self.curr_block.y
                    if y <= self.height:
                        self.pool[y][x] = 1
                self.curr_block = None

                # 消行
                self.pool = [
                    line for line in self.pool if sum(line) < self.width
                ]
                nline = self.height + 1 - len(self.pool)
                for _ in range(nline):
                    self.pool.append([0] * self.width)
                self.event_clear(nline)

                # 终局判断
                if any(self.pool[-1]):
                    self.running = 0
                    return self.event_end()

            # 方块移动
            else:
                self.block_settled = not self.try_move(
                    (self.curr_block.x, self.curr_block.y - 1))

        # 方块生成
        if not self.curr_block:
            self.curr_block = self.next_block.pop(0)
            self.next_block.append(self.block_seq.pop())
            self.curr_block.x = self.width // 2
            self.curr_block.y = self.height
            self.block_settled = False

        # 绘制事件
        self.event_draw()

    def event_end(self):
        """ 游戏结束事件 """
        pass


if __name__ == '__main__':
    tmp = RandSeq(lambda: random.randrange(7))
    tmp2 = RandSeq(lambda: random.randrange(7))
    print(*(tmp.pop() for i in range(30)))
    print(*(tmp2.pop() for i in range(30)))