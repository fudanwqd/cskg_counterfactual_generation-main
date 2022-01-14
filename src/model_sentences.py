w = open('data/common_sense_sentences.dataset', 'w', encoding='utf-8')

# for test
# with open('data/cskg_small.tsv', 'r', encoding='utf-8') as f:

with open('data/cskg.tsv', 'r', encoding='utf-8') as f:
    next(f)    
    for line in f:
        line_list = line.strip().split('\t')
        if len(line_list) < 10:
            continue
        # w.write(line_list[9].replace('[[', '').replace(']]', '') + '\n')
        w.write(line_list[9] + '\n')

w.close()
