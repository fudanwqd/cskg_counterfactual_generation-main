# node1 is `bus|front bus|sitting|train|transit`, node2 is `car|cars|green truck|is|pick up|pickup truck|small car|truck|vehicle|white car`, relation is `across from|across street from|and|are next to|back of|behind a|behind blue|behind|beside|between|by|close to|crosses|driving behind|driving beside a|driving next to|driving past|driving|ear|following|front of|hits|in front of a|in front of|left of|near a|near|nex to|next to a|next to|next|on front of|on side of|on side|on|parked beside|parked near|passing|stopped behind|stopped beside|to right of|trailing|turning away from|visible beside|waiting for`
# ll is short for line_list

entity_set = set()

w_entity = open('data/cskg_entity.csv', 'w', encoding='utf-8')
w_relation = open('data/cskg_relation.csv', 'w', encoding='utf-8')

w_entity.write("entityID:ID\tcontent\t:LABEL\n") 
w_relation.write(":START_ID\t:END_ID\t:TYPE\n") 

def deal_with_one_relation(node1, node2, relation, node1id, node2id):
    if node1id not in entity_set:
        w_entity.write(node1id + '\t' + node1 + '\tEntity\n')
        entity_set.add(node1id)
    if node2id not in entity_set:
        w_entity.write(node2id + '\t' + node2 + '\tEntity\n')
        entity_set.add(node2id)

    w_relation.write(node1id + '\t' + node2id + '\t' + relation + '\n')

# for test
with open('data/cskg_small.tsv', 'r', encoding='utf-8') as f:
# with open('data/cskg.tsv', 'r', encoding='utf-8') as f:
    next(f)    
    for line in f:
        line_list = line.strip().split('\t')

        relation_type = line_list[6].replace('\\', '').replace("'", "").replace('"', '')
        if relation_type == '':
            continue

        node1 = line_list[4].replace('\\', '').replace("'", "").replace('"', '')
        node2 = line_list[5].replace('\\', '').replace("'", "").replace('"', '')
        
        a_l = node1.split('|')
        b_l = node2.split('|')
        c_l = relation_type.split('|')

        for aa in a_l:  # node1
            for bb in b_l:  # node2                
                for cc in c_l:  # relation
                    aa_id = line_list[1] if len(a_l) == 1 else line_list[1]+'/'+aa.replace(' ', '_')
                    bb_id = line_list[3] if len(b_l) == 1 else line_list[3]+'/'+aa.replace(' ', '_')
                    
                    deal_with_one_relation(aa, bb, cc, aa_id, bb_id)
        

w_relation.close()
