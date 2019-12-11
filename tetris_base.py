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
        if self.type in 'IZS' and not (self.phase ^ back):  # 中心对称方块
            back = not back

        if back:  # 正旋转
            self.phase += 1
            self.outers = tuple((y, -x) for x, y in self.outers)
        else:  # 反旋转
            self.phase -= 1
            self.outers = tuple((-y, x) for x, y in self.outers)

        self.phase %= 4

    def copy(self):
        """ 复制当前块 """
        block = Block(self.BLOCK_NAMES.index(self.type))
        while block.phase != self.phase:
            block.rotate()
        block.x, block.y = self.x, self.y
        return block

    def __iter__(self):
        """ 迭代获取所有块相对中心位置偏移 """
        yield (0, 0)
        yield from self.outers


class TetrisDraw:
    """
    游戏绘制类
    dump_*: 输出文本
    """

    def dump_lines(self):
        """ 将游戏场地逐行返回为字符串列表 """
        lines = ['==' * (1 + self.width)]
        if not self.running:
            lines[0] = 'GAME  OVER'.center(2 + 2 * self.width, '=')
        pool_tmp = [['[]' if x else '  ' for x in self.pool[i]]
                    for i in range(self.height)]
        if self.curr_block:
            for pos in self.curr_block:
                x = pos[0] + self.curr_block.x
                y = pos[1] + self.curr_block.y
                if y >= self.height:
                    continue
                pool_tmp[y][x] = '<>'
        lines.extend(('|%s|' % (''.join(x))) for x in reversed(pool_tmp))
        lines.append(lines[0])

        return lines

    def dump_info(self):
        """ 返回当前游戏状态说明文字 """
        res = f'score:{self.score}'
        if self.running:
            res += (f' curr:{self.curr_block and self.curr_block.type}'
                    f' next:{"+".join(x.type for x in self.next_block)}')
        else:
            res += ' Game Over'
        return res


class TetrisLogic(TetrisDraw):
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
        self.paused = False  # 暂停模式，屏蔽玩家操作
        self.pool = [[0] * self.width
                     for _ in range(self.height + 1)]  # 游戏场地，顶行用于判断死亡
        self.curr_block = None  # 当前方块
        self.block_settled = False  # 游戏逻辑中下回合放置当前控制方块
        self.score = 0

        # 生成方块序列
        self.block_seq = RandSeq(Block.get, self.seed)
        self.next_block = [self.block_seq.pop(), self.block_seq.pop()]

        # 底部出行序列
        self.grow_seq = RandSeq(
            lambda: [random.random() > 0.3 for i in range(self.width)],
            self.seed)

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
        if not self.curr_block or self.paused:
            return
        if self.try_move((self.curr_block.x - 1, self.curr_block.y)):
            self.block_settled = False
            self.event_draw()

    def control_right(self, *a):
        if not self.curr_block or self.paused:
            return
        if self.try_move((self.curr_block.x + 1, self.curr_block.y)):
            self.block_settled = False
            self.event_draw()

    def control_rotate(self, *a):
        if not self.curr_block or self.paused:
            return
        if self.try_rotate():
            self.block_settled = False
            self.event_draw()

    def control_swap(self, *a):
        if self.paused:
            return
        self.next_block = self.next_block[::-1]
        self.event_draw()

    def event_add_line(self):
        """ 底部添加随机行 """
        tmp = self.grow_seq.pop()
        while not 0 < sum(tmp) < self.width:  # 防止生成空行/满行
            tmp = self.grow_seq.pop()
        self.pool.insert(0, tmp)
        self.pool.pop()
        if self.curr_block:
            self.curr_block.y += 1

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


class TetrisLogicFrame(TetrisLogic):
    """ 按帧更新的俄罗斯方块逻辑 """
    NFRAME = 10
    NFRAME_SPEEDUP = 1

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


class TetrisLogicVersus(TetrisLogicFrame):
    """ 按帧更新的俄罗斯方块逻辑 对战版 """

    def __init__(self, root, score_per_line=10, *a, **kw):
        super().__init__(root, *a, **kw)

        self.opponent = None  # 对手游戏逻辑
        self.score_counter = 0
        self.dscore = max(score_per_line, 1)

    def event_clear(self, n):
        """
        根据得分给对方场地添加新行
        多重消除增加更多行
        """
        super().event_clear(n)
        if self.opponent:
            for i in range(n - 1):
                self.opponent.event_add_line()
            while self.score_counter + self.dscore <= self.score:
                self.score_counter += self.dscore
                self.opponent.event_add_line()


### AI接口


class TetrisAI:
    """俄罗斯方块AI接口
    由TetrisLogicAuto类
    """

    def __init__(self, width, height):
        """ 初始化接收场地宽高 """

    def evaluate(self, block, pool):
        """
        AI执行接口
        block: 当前方块的副本
        pool: 当前游戏场地的副本
        """

    def event_clear(self, n):
        """ 消除行时通知事件 """


class TetrisLogicAuto(TetrisLogicVersus):
    """按帧更新的俄罗斯方块逻辑 自动控制版
    通过接入并定时调用AI接口实现控制游戏运行
    """

    NFRAME_AI = 5

    def __init__(self, AI_class, *a, **kw):
        super().__init__(*a, **kw)

        self.OPERATIONS = {# 操作功能
            'a': self.control_left,
            'd': self.control_right,
            'w': self.control_rotate,
            's': self.control_speedup,
            'n': self.control_speeddown,
            'p':self.control_swap,
        }
        self.AI = AI_class(self.width, self.height)  # 自动控制模块
        self.ai_frame_counter = 0  # AI帧计数器

    def event_update_frame(self):
        """ 按帧更新AI """
        super().event_update_frame()

        self.ai_frame_counter -= 1
        if self.ai_frame_counter <= 0:
            self.ai_frame_counter = self.NFRAME_AI
            try:
                event = self.AI.evaluate(self.curr_block
                                         and self.curr_block.copy(),
                                         [x[:] for x in self.pool])
                for e in set(event):
                    e = self.OPERATIONS.get(e)
                    if e:
                        e()
            except Exception as e:
                print(f'AI ERROR|{type(e).__name__}: {e}')

    def event_clear(self, n):
        """ 通知AI行消除 """
        super().event_clear(n)
        self.AI.event_clear(n)
