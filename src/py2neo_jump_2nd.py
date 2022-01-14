from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher 
import random
import re


# 运行代码前，必须打开 neo4j
graph = Graph('http://localhost:7474', auth=('neo4j', '123456'))

# 基于距离：超过几跳可以生成反事实
## 1. 遍历所有拥有 sentence 的节点
relation_matcher = RelationshipMatcher(graph)
# relations_with_sentece = (relation_matcher.match(None, None).limit(5)).where(sentence='NoneSentence')
relations_with_sentece = relation_matcher.match(None, None).where("_.sentence <> 'NoneSentence'").limit(5000)
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

## 4. 从实体集合中随机取一个实体，来对主语或者宾语进行替换。这个实体离被替换的实体的距离，目前设置的是两跳。
len_relation_dict = len(relation_dict)
len_subjects = len(subject_dict)
len_objects = len(object_dict)
subject_list = list(subject_dict)
object_list = list(object_dict)

## 4.1 随机抽取一个关系
def get_random_relation(relation_dict):
    while(True):
        relation_name_key = random.sample(relation_dict.keys(), 1)[0]
        # random_subject_set, random_object_set = relation_dict[relation_name_key]
        random_subject_set, random_object_set = relation_dict.pop(relation_name_key)
        if len(random_subject_set) > 5 and len(random_object_set) > 5:
            break
    random_relation = relation_matcher.match(None, r_type=relation_name_key).where("_.sentence <> 'NoneSentence'").first()
    random_relation_start_node = random_relation.start_node
    random_relation_end_node = random_relation.end_node
    random_sentence = random_relation['sentence']
    return random_subject_set, random_object_set, random_relation_start_node, random_relation_end_node, random_sentence

node_matcher = NodeMatcher(graph)
def id_2_node(id):
    node = node_matcher.match("Entity").where("_.entityID = '" + id + "'").first()
    return node

def is_distance_two_jumps(node1, node2):
    relations = relation_matcher.match([node1, node2], None)
    if len(relations) > 0:
        return False
    return True

## 4.2 随机抽取一个 subject 实体，距离 start_node 有两跳关系
def get_random_subject_content(random_subject_set, subject_node):
    if subject_node['entityID'] in random_subject_set:
        random_subject_set.remove(subject_node['entityID'])
    while(True):
        random_subject_idx = random.randint(0, len_subjects - 1)
        random_subject_id = subject_list[random_subject_idx]
        if is_distance_two_jumps(subject_node, id_2_node(random_subject_id)):
            break
    random_subject_alternative = subject_dict[random_subject_id]
    random_replaced_subject_content = random_subject_alternative['content']
    return random_replaced_subject_content

## 4.2 随机抽取一个 object 实体，距离 end_node 有两跳关系
def get_random_object_content(random_object_set, object_node):
    if object_node['entityID'] in random_object_set:
        random_object_set.remove(object_node['entityID'])
    while(True):
        random_object_idx = random.randint(0, len_objects - 1)
        random_object_id = object_list[random_object_idx]
        if is_distance_two_jumps(object_node, id_2_node(random_object_id)):
            break
    random_object_alternative = object_dict[random_object_id]
    random_replaced_object_content = random_object_alternative['content']
    return random_replaced_object_content

## 5. 生成从上述 relation 附着的句子上替换后的句子
def replace_entity(sentence, replaced_entity_content, head_flag=True):
    pattern = re.compile(r'\[\[(.*?)\]\]')   
    head = pattern.search(sentence)
    head_start_idx = head.span()[0]
    head_end_idx = head.span()[1]

    if head_flag: 
        return sentence[0:head_start_idx + 2] + replaced_entity_content + sentence[head_end_idx - 2:]
    else:
        tail = pattern.search(sentence, head_end_idx)
        tail_start_idx = tail.span()[0]
        tail_end_idx = tail.span()[1]
        return sentence[0:tail_start_idx + 2] + replaced_entity_content + sentence[tail_end_idx - 2:]


for i in range(5):
    random_subject_set, random_object_set, random_relation_start_node, random_relation_end_node, random_sentence = get_random_relation(relation_dict)

    random_replaced_subject_content = get_random_subject_content(random_subject_set, random_relation_start_node)
    random_replaced_object_content = get_random_object_content(random_object_set, random_relation_end_node)

    print('origin:\t\t', random_sentence)

    generated_sentence_s = replace_entity(random_sentence, random_replaced_subject_content, True)
    print('replace s:\t', generated_sentence_s)

    generated_sentence_o = replace_entity(random_sentence, random_replaced_object_content, False)
    print('replace o:\t', generated_sentence_o)

    print('-' * 10)
