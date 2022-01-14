import linecache
import random
import re

import numpy as np
from py2neo import Graph, Node, Relationship

f = open('data/common_sense_sentences.dataset', 'r')
graph = Graph('http://localhost:7474', auth=('neo4j', '1234'))

import os


def test(num):
    lines = []
    # print(os.path.getsize('data/common_sense_sentences.txt'))
    line = f.readline()
    while line:
        # print(line)
        if random.random() < 1:
            lines.append(line)
        if len(lines) == num:
            break
        line = f.readline()
    return lines


def test2(num):
    lines = []
    for i in range(num):
        # 随机获取一行数据
        lineNumber = random.randint(1, 604768)  # 随机数作为行数
        line = linecache.getline('data/common_sense_sentences.dataset', lineNumber)  # 随机读取一行
        if len(line) == 0:  # 过滤为空的内容
            continue
        # 写入新的一个文件
        lines.append(line)

    # 不再读取时，需要清除缓存
    linecache.clearcache()
    return lines


def find_antonyms(word):
    words = []
    data = graph.run("match path=(n:Entity)-[r:antonym]->(m:Entity) "
                     "where n.content = $id return m.content",
                     id=word)
    for w in data:
        words.append(w["m.content"])
    data2 = graph.run("match path=(m:Entity)-[r:antonym]->(n:Entity) "
                      "where n.content = $id return m.content",
                      id=word)
    for w in data2:
        if w["m.content"] not in words:
            words.append(w["m.content"])
    return words


def make(sentence):
    pattern = re.compile(r"[\[]+(.*?)[\]]+")
    nodes = re.findall(pattern, sentence)
    result = []
    for node in nodes:
        antonyms = find_antonyms(node)
        for w in antonyms:
            node_word = "[[" + node + "]]"
            w_word = "[[" + w + "]]"
            s = sentence.replace(node_word, w_word)
            result.append(s)
    return result


if __name__ == '__main__':
    # make("[[0]] is similar to [[cardinal]]")
    # exit(1)
    data = test2(1000)
    # print(data)
    result = []
    for d in data:
        d = d.strip()
        print("raw text:", d)
        print("counterfactual:")
        counterfactual = make(d)
        print(counterfactual)
        result.extend(counterfactual)
        print("==========")
    fh = open("./data/counterfactual.txt", 'w')
    for l in result:
        fh.write(l+"\n")
    fh.close()
    exit(0)
    sen = "[[0]] is the [[empty set]]."
    l = make(sen)
    print(l)
# with open('ckg.txt', 'r' ,encoding='utf-8') as f:
#     for line in f:
#         line_list = line.strip().split(',')
#         name1 = line_list[0]
#         name2 = line_list[2]
#         rela = line_list[1]
#         node1 = Node('ckg_entity', qualified_name=name1)
#         node2 = Node('ckg_entity', qualified_name=name2)
#         relation = Relationship(node1, rela, node2)
#         graph.merge(node1,'ckg_entity', 'qualified_name')
#         graph.merge(node2,'ckg_entity', 'qualified_name')
#         graph.merge(relation,'ckg_entity', 'qualified_name')
