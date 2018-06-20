# coding=utf-8


class Node:  # 结点
    def __init__(self, key, weight):
        self.key = key
        self.weight = weight
        self.cur_weight = 0

