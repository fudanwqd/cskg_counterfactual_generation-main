
def sample_sense():
    import random

    with open('dataset/common-sense-for-knowledge.dataset') as f:
        origins2 = [line for line in f.readlines() if len(line.replace('\n', '')) > 0]

    with open('dataset/common-sense-for-rule.dataset') as f:
        origins3 = [line for line in f.readlines() if len(line.replace('\n', '')) > 0]

    with open('dataset/common-sense.dataset') as f:
        origin_lines = [line for line in f.readlines() if len(line.replace('\n', '')) > 0]
        lines = origins2 + origin_lines
        index = list(range(len(origins2), len(origins2) + len(origin_lines)))
        random.shuffle(index)
        index = list(range(0, len(origins2))) + index

        with open('dataset/knowledge-gen-non-sense.dataset') as f:
            lines2 = [line for line in f.readlines() if len(line.replace('\n', '')) > 0]
            index2 = list(range(0, len(lines2)))
            random.shuffle(index2)

            with open('dataset/train-knowledge-gen.dataset', 'w') as fw:
                for idx1, idx2 in zip(index[:10000], index2[:10000]):
                    fw.write(lines[idx1].replace('[','').replace(']','').replace('\n', '') + '\t0\n')
                    fw.write(lines2[idx2].replace('[','').replace(']','').replace('\n', '') + '\t1\n')

            with open('dataset/validate-knowledge-gen.dataset', 'w') as fw:
                for idx2 in index2[10000:]:
                    fw.write(lines2[idx2].replace('[','').replace(']','').replace('\n', '') + '\t1\n')

        lines = origins3 + origin_lines
        index = list(range(len(origins3), len(origins3) + len(origin_lines)))
        random.shuffle(index)
        index = list(range(0, len(origins3))) + index

        with open('dataset/rule-gen-non-sense.dataset') as f:
            lines3 = [line for line in f.readlines() if len(line.replace('\n', '')) > 0]
            index3 = list(range(0, len(lines3)))
            random.shuffle(index3)

            with open('dataset/validate-rule-gen.dataset', 'w') as fw:
                for idx3 in index3[10000:]:
                    fw.write(lines3[idx3].replace('[', '').replace(']', '').replace('\n', '') + '\t1\n')

            with open('dataset/train-rule-gen.dataset', 'w') as fw:
                for idx1, idx3 in zip(index[:10000], index3[:10000]):
                    fw.write(lines3[idx3].replace('[', '').replace(']', '').replace('\n', '') + '\t1\n')
                    fw.write(lines[idx1].replace('[', '').replace(']', '').replace('\n', '') + '\t0\n')

        with open('dataset/validate-common-sense.dataset', 'w') as fw:
            for idx in index[10000:15000]:
                fw.write(lines[idx].replace('[', '').replace(']', '').replace('\n', '') + '\t0\n')

sample_sense()