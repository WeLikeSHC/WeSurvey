# coding=utf-8

"""

平滑加权负载均衡算法

"""


class Node:  # 结点
    def __init__(self, key, weight):
        self.key = key
        self.weight = weight
        self.cur_weight = 0


class NodeList:

    def __init__(self):
        self.__node = list()
        self.__length = 0
        self.__keys = set()
        self.__current = 0

    def add(self, _node):
        if _node.key not in self.__keys:
            self.__node.append(_node)
            self.__keys.add(_node.key)
            self.__length += 1
        else:
            raise Exception("key {} has already existed!".format(_node.key))

    def __get_next_index(self):  # 先找到权重最大的结点分配给其任务 然后降低其权重

        total = 0
        _index = -1
        for _i in range(self.__length):
            self.__node[_i].cur_weight += self.__node[_i].weight
            total += self.__node[_i].weight
            if _index == -1 or self.__node[_index].cur_weight < self.__node[_i].cur_weight:
                _index = _i

        self.__node[_index].cur_weight -= total
        return _index

    def __getattr__(self, item):  # 获取给定属性的值
        if item == 'next':
            return self.__get_next_index()
        elif item == 'length':
            return self.__length
        else:
            raise AttributeError(item)

    def __getitem__(self, item):  # 支持下标直接引用
        return node_list.__node[item]

    def __iter__(self):  # 使其本身成为迭代对象
        return iter(self.__node)


if __name__ == '__main__':
    node_list = NodeList()
    node1 = Node(1, 2)
    node2 = Node(2, 3)
    node3 = Node(3, 4)
    node_list.add(node1)
    node_list.add(node2)
    node_list.add(node3)
    print node_list.length
    for i in range(9):
        index = node_list.next
        print node_list[index].key, node_list[index].weight
