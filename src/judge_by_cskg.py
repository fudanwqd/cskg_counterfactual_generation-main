from py2neo import Graph

graph = Graph('http://localhost:7474', auth=('neo4j', '123456'))

f = open('data/output_sentences.dataset')
node1 = ""
node2 = ""
relation = ""
for data in f.readlines():
    print(data.replace("\n",""))
    a = data.find("[[")
    b = data.find("]]")
    node1 = data[a+2:b]
    data = data[b+3:]
    c = data.find("[[")
    d = data.find("]]")
    relation = data[:c-1]
    node2 = data[c+2:d]
    if node1!="" and node2!="" and relation!="":
        cypher = "MATCH p=(:Entity{content:'" + node1 +"'})-[r:`" + relation +"`]->(:Entity{content:'" + node2 + "'}) RETURN p"
        print(cypher)
        find_rela = graph.run(cypher)
        result = find_rela.data()

        if len(result) == 0:
            print("数据库中不存在，是反事实")
        else:
            print("数据库中存在，不是反事实")


