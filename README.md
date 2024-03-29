# yTetris
基于Python的俄罗斯方块框架

## 基础模块`tetris_base.py`
基础模块，包含俄罗斯方块游戏逻辑

1. ### 功能总览
    1. 基于种子确定的随机方块序列生成
    1. 游戏操作逻辑（左右移动、旋转）
    1. 游戏规则逻辑（方块下落、消行、得分统计、超过边界后游戏结束）

1. ### 代码结构 TODO
    1. #### 随机序列生成器`RandSeq`
    1. #### 方块类`Block`
    1. #### 游戏逻辑类`TetrisLogic`
    1. #### 游戏逻辑类`TetrisLogicFrame`
    1. #### 游戏逻辑类`TetrisLogicVersus`
    1. #### AI接口类`TetrisAI`
    1. #### AI游戏逻辑类`TetrisLogicAuto`

## 游戏实现
1. `tetris_ascii.py`  
    基于tkinter模块实现的单人俄罗斯方块游戏  
    更新逻辑使用Tk.after事件实现  
    初步实现 __能玩儿__ 目标

1. `tetris_ascii_frame.py`  
    ASCII俄罗斯方块-帧更新版  
    相对于`tetris_ascii.py`增加实现了 __基于帧更新__ 的实时游戏逻辑  
    在加速下落事件上操作更流畅

1. `tetris_ascii_versus.py`  
    ASCII俄罗斯方块-对战版  
    在`tetris_ascii_frame.py`基础上增加了双人对战、 __向对手场地添加行__ 的功能

1. `tetris_ascii_pve.py`  
    ASCII俄罗斯方块-人机对战版  
    在`tetris_ascii_versus.py`基础上实现了人机对战、 __AI接口__ 功能

## 其它
1. `tetris_ai_examples.py`  
    预置的示例AI实现