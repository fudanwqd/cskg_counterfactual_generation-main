entity_set = set()
w_entity = open('data/cskg_entity_sentence.csv', 'w', encoding='utf-8')
w_relation = open('data/cskg_relation_sentence.csv', 'w', encoding='utf-8')

w_entity.write("entityID:ID\tcontent\t:LABEL\n") 
w_relation.write(":START_ID\t:END_ID\t:TYPE\tsentence\n") 

# for test
# with open('data/cskg_small.tsv', 'r', encoding='utf-8') as f:

with open('data/cskg.tsv', 'r', encoding='utf-8') as f:
    next(f)    
    for line in f:
        line_list = line.strip().split('\t')

        relation_type = line_list[6].replace('\\', '').replace("'", "").replace('"', '')
        if relation_type == '':
            continue

        node1 = line_list[4].replace('\\', '').replace("'", "").replace('"', '')
        node2 = line_list[5].replace('\\', '').replace("'", "").replace('"', '')

        if line_list[1] not in entity_set:
            w_entity.write(line_list[1] + '\t' + node1 + '\tEntity\n')
            entity_set.add(line_list[1])
        if line_list[3] not in entity_set:
            w_entity.write(line_list[3] + '\t' + node2 + '\tEntity\n')
            entity_set.add(line_list[3])

        sent = "NoneSentence" if len(line_list) < 10 else line_list[9]

        w_relation.write(line_list[1] + '\t' + line_list[3] + '\t' + relation_type + '\t' + sent + '\n')

w_relation.close()
