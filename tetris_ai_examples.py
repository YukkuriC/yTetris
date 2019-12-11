from tetris_base import TetrisAI
import random, collections


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


class PierreDellacherie(TetrisAI):
    """ 基于Pierre Dellacherie估值的俄罗斯方块AI """

    def __init__(self, width, height):
        """ 声明状态记录变量 """
        self.width, self.height = width, height

    def try_move(self, block, pool, x, y):
        """
        尝试移动砖块至场地位置，判断可行性
        """
        # 判断场地相交
        try:
            for offset in block:
                nx, ny = x + offset[0], y + offset[1]
                if not (0 <= nx < self.width and 0 <= ny):
                    # print((x,y),(nx,ny))
                    return False
                if ny > self.height:  # 无上界
                    continue
                if pool[ny][nx]:
                    return False
        except (IndexError, AssertionError):
            return False

        # 移动方块
        block.x, block.y = x, y
        return True

    def set_block(self, block, pool, value):
        """
        铺砖或回收
        Returns:
            按行统计的铺砖个数字典
        """
        res = collections.Counter()
        for offset in block:
            nx, ny = block.x + offset[0], block.y + offset[1]
            if ny > self.height:  # 无上界
                continue
            pool[ny][nx] = value
            res[ny] += 1
        # 返回统计值
        return res

    def evaluate(self, block, pool):
        """ 执行函数，遍历可行放置位置并返回操作序列 """
        if not block:
            return ''

        mblock = self.get_best_drop(block, pool)

        # 计算动作
        hmove = 'ad' [mblock.x > block.x] if mblock.x != block.x else ''
        r = 'w' if mblock.phase != block.phase else ''
        return hmove + r

    def get_best_drop(self, original_block, pool):
        """ 遍历可能落点确定最优位置 """
        block = original_block.copy()  # 复制块用于查找
        nphase = 1 if block.type == 'O' else 2 if block.type in 'IZS' else 4  # 当前块可用旋转数
        mblock, mvalue = None, (-1e10, 1e10)  # 最优估值 (PD值、操作距离)

        for dphase in range(nphase):
            # 寻找可下落位置
            for tx in range(self.width):
                if not self.try_move(block, pool, tx, original_block.y):
                    continue

                # 模拟下落
                ty = original_block.y
                while self.try_move(block, pool, tx, ty - 1):
                    ty -= 1

                # 选择全局最大估值
                pd_value = self.calc_pd(block, pool)
                pd_value = (pd_value,
                            -100 * abs(block.x - original_block.x) - dphase)
                if pd_value > mvalue:
                    mblock, mvalue = block.copy(), pd_value

            # 旋转
            block.rotate()

        return mblock

    def calc_pd(self, block, pool):
        """
        评估当前局面pd估值
        估值期间block位置不更改
        """
        # 铺方块
        block_set = self.set_block(block, pool, 1)

        # 计算估值
        landingHeight = block.y  # landingHeight
        ero1 = ero2 = 0  # erodedPieceCellsMetric
        boardRowTransitions = 0  # boardRowTransitions
        boardColTransitions = 0  # boardColTransitions
        boardBuriedHoles = 0  # boardBuriedHoles
        boardWells = 0  # boardWells

        # 行统计
        for i, line in enumerate(pool):
            ncell = 0
            for j, cell in enumerate(line):
                ncell += cell
                if j and (cell ^ last_cell):
                    boardRowTransitions += 1
                    if cell and (j == 1 or line[j - 2]):  # 1,0,1
                        boardWells += 1
                last_cell = cell

            # 右侧井
            if line[-2] and not line[-1]:
                boardWells += 1

            if ncell == self.width:  # 消行统计
                ero1 += 1
                ero2 += block_set[i]
            elif ncell == 0:  # 出现空行跳出
                break

        # 列统计
        maxHeight = i + 1
        for x in range(self.width):
            hole_counter = 0
            for y in range(maxHeight):
                cell = pool[y][x]

                if cell:  # 洞
                    boardBuriedHoles += hole_counter
                    hole_counter = 0
                else:
                    hole_counter += 1

                if y and cell ^ last_cell:  # 列变换
                    boardColTransitions += 1
                last_cell = cell

        # 回收方块
        self.set_block(block, pool, 0)
        # 返回估值
        erodedPieceCellsMetric = ero1 * ero2
        return -45 * landingHeight + 34 * erodedPieceCellsMetric - 32 * boardRowTransitions - 93 * boardColTransitions - 79 * boardBuriedHoles - 34 * boardWells


class PDFast(PierreDellacherie):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        # 状态量
        # 0: 待评估场地
        # 1: 已评估，待执行动作
        # 2: 动作执行完毕，待加速
        # 3: 加速完毕，需减速评估场地
        self.phase = 0

        # 动作队列
        self.hmove = self.hcount = 0  # 平移
        self.rcount = 0  # 旋转

    def evaluate(self, block, pool):
        if not block:
            return ''

        print(self.phase, self.hmove, self.hcount, self.rcount)

        res = ''  # 本回合输出的操作

        if self.phase == 3:  # 减速
            res += 'n'
            self.phase = 0

        if self.phase == 0:  # 评估场地生成动作序列

            mblock = self.get_best_drop(block, pool)

            # 计算动作
            self.hmove = 'ad' [mblock.x > block.x]
            self.hcount = abs(mblock.x - block.x)
            self.rcount = (block.phase - mblock.phase) % 4
            if block.type in 'IZS':
                self.rcount %= 2
            self.phase = 1

        if self.phase == 1 and block.y < self.height:  # 按动作队列输出
            if self.hcount > 0:
                self.hcount -= 1
                res += self.hmove
            if self.rcount > 0:
                res += 'w'
                self.rcount -= 1

            # 空队列时状态转移
            if self.rcount + self.hcount == 0:
                self.phase = 2

        if self.phase == 2:  # 加速
            res += 's'

        return res

    def event_clear(self, n):
        """ 结束加速，返回评估态 """
        self.phase = 3
