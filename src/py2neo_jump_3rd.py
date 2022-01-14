from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher 
import random
import re


# 运行代码前，必须打开 neo4j
graph = Graph('http://localhost:7474', auth=('neo4j', '123456'))

# 基于距离：超过几跳可以生成反事实
## 1. 遍历所有拥有 sentence 的节点
relation_matcher = RelationshipMatcher(graph)
# relations_with_sentece = (relation_matcher.match(None, None).limit(5)).where(sentence='NoneSentence')
relations_with_sentece = relation_matcher.match(None, None).where("_.sentence <> 'NoneSentence'").limit(10000)
# relations_with_sentece = relation_matcher.match(None, None).where("_.sentence <> 'NoneSentence'")

## 2. 获取其中的关系 relation，目的是为了记住句子的模样从而方便套上去，设置一个 map {relation_id, [(该关系下的主语集合), (该关系下的宾语集合)]}
relation_dict = {}

## 3. 构建主语集合和宾语集合
subject_dict = {}
object_dict = {}

for relation_with_sentece in list(relations_with_sentece):
    if relation_with_sentece['sentence'] == 'NoneSentence':
        continue
    relation_name = type(relation_with_sentece).__name__
    # the relationship must be one relationship
    if relation_name.find('|') > 0:
        continue

    relationship_start_node = relation_with_sentece.start_node
    relationship_start_node_id = relation_with_sentece.start_node['entityID']
    relationship_end_node = relation_with_sentece.end_node
    relationship_end_node_id = relation_with_sentece.end_node['entityID']

    if relation_name in relation_dict:
        relationship_subject_set, relationship_object_set = relation_dict.get(relation_name)
        relationship_subject_set.add(relationship_start_node_id)
        relationship_object_set.add(relationship_end_node_id)
    else:
        relationship_subject_set = set()
        relationship_object_set = set()
        relationship_subject_set.add(relationship_start_node_id)
        relationship_object_set.add(relationship_end_node_id)
        relation_dict[relation_name] = [relationship_subject_set, relationship_object_set]

    subject_dict[relationship_start_node_id] = relationship_start_node
    object_dict[relationship_end_node_id] = relationship_end_node

## 4. 对主语或者宾语进行替换。这个实体离被替换的实体的距离，目前设置的是两跳。

## 4.1 抽取一个关系
def get_one_relation(relation_name_key):
    relation_name_key = random.sample(relation_dict.keys(), 1)[0]
    random_subject_set, random_object_set = relation_dict.pop(relation_name_key)
    random_relation = relation_matcher.match(None, r_type=relation_name_key).where("_.sentence <> 'NoneSentence'").first()
    random_sentence = random_relation['sentence']
    return random_subject_set, random_object_set, random_sentence

node_matcher = NodeMatcher(graph)
def id_2_node(id):
    node = node_matcher.match("Entity").where("_.entityID = '" + id + "'").first()
    return node

def is_distance_two_jumps(node1, node2):
    relations = relation_matcher.match([node1, node2], None)
    if len(relations) > 0:
        return False
    return True

## 5. 生成从上述 relation 附着的句子上替换后的句子
def replace_entity(sentence, head_entity, tail_entity):
    pattern = re.compile(r'\[\[(.*?)\]\]')   

    head = pattern.search(sentence)
    head_start_idx = head.span()[0]
    head_end_idx = head.span()[1]

    tail = pattern.search(sentence, head_end_idx)
    tail_start_idx = tail.span()[0]
    tail_end_idx = tail.span()[1]

    return sentence[0:head_start_idx + 2] + head_entity + sentence[head_end_idx - 2:tail_start_idx + 2] + tail_entity + sentence[tail_end_idx - 2:]

w = open('data\counterfactual_3rd.dataset', 'w', encoding='utf-8')
print(len(relation_dict))

relation_dict_key_list = list(relation_dict.keys())
for i in range(len(relation_dict_key_list)):
    random_subject_set, random_object_set, random_sentence = get_one_relation(relation_dict_key_list[i])
    # 替换
    for s in random_subject_set:
        if s.find("'") >= 0:
            continue
        for o in random_object_set:
            if o.find("'") >= 0:
                continue
            if is_distance_two_jumps(id_2_node(s), id_2_node(o)):
                o_content = object_dict[o]['content']
                s_content = subject_dict[s]['content']
                sen = replace_entity(random_sentence, s_content, o_content)
                w.write(sen + '\n')
    
w.close()
