# Counterfactual Judgement and Generation based on Commonsense Knowledge Graph

基于常识知识图谱的反事实判断与生成

> 更新于2021年12月28日

# 一、构建常识知识图谱

## 1. 数据集简介

基于论文 [CSKG: The CommonSense Knowledge Graph](https://arxiv.org/abs/2012.11490)，我们获取了其提供的[数据集](https://zenodo.org/record/4331372#.YcPjzGhByHs) CSKG（**C**ommon**s**ense **K**nowledge **G**raph）。

该数据集来源于 7 个国际认可度较高的数据资源，如 ConceptNet 和 wikidata 等，包含六百多万条语句和200多个节点。

## 2. 数据集预处理

#### （1）数据一览

数据集中包含字段前 20 行如下（已舍去 `ID` 和 `relation;dimension`）：


| node1                   | relation       | node2                            | node1;label       | node2;label                | relation;label | source | sentence                                 |
| ----------------------- | -------------- | -------------------------------- | ----------------- | -------------------------- | -------------- | ------ | ---------------------------------------- |
| /c/en/0                 | /r/DefinedAs   | /c/en/empty_set                  | 0                 | empty set                  | defined as     | CN     | [[0]] is the [[empty set]].              |
| /c/en/0                 | /r/DefinedAs   | /c/en/first_limit_ordinal        | 0                 | first limit ordinal        | defined as     | CN     | [[0]] is the [[first limit ordinal]].    |
| /c/en/0                 | /r/DefinedAs   | /c/en/number_zero                | 0                 | number zero                | defined as     | CN     | [[0]] is the [[number zero]].            |
| /c/en/0                 | /r/HasContext  | /c/en/internet_slang             | 0                 | internet slang             | has context    | CN     |                                          |
| /c/en/0                 | /r/HasProperty | /c/en/pronounced_zero            | 0                 | pronounced zero            | has property   | CN     | [["0"]] is [[pronounced zero]]           |
| /c/en/0                 | /r/IsA         | /c/en/set_containing_one_element | 0                 | set containing one element | is a           | CN     | [[{0}]] is a type of [[set containing one element]]. |
| /c/en/0                 | /r/RelatedTo   | /c/en/1                          | 0                 | 1                          | related to     | CN     |                                          |
| /c/en/0                 | /r/RelatedTo   | /c/en/2                          | 0                 | 2                          | related to     | CN     |                                          |
| /c/en/0.22_inch_calibre | /r/IsA         | /c/en/5.6_millimetres            | 0.22 inch calibre | 5.6 millimetres            | is a           | CN     | [[0.22 inch calibre]] is [[5.6 millimetres]] |
| /c/en/0/a/wn            | /r/SimilarTo   | /c/en/cardinal/a/wn              | 0                 | cardinal                   | similar to     | CN     | [[0]] is similar to [[cardinal]]         |
| /c/en/0/n               | /r/Antonym     | /c/en/1                          | 0                 | 1                          | antonym        | CN     |                                          |
| /c/en/0/n               | /r/HasContext  | /c/en/electrical_engineering     | 0                 | electrical engineering     | has context    | CN     |                                          |
| /c/en/0/n               | /r/RelatedTo   | /c/en/low                        | 0                 | low                        | related to     | CN     |                                          |
| /c/en/0/n/wn/quantity   | /r/Synonym     | /c/en/zero/n/wn/quantity         | 0                 | zero                       | synonym        | CN     | [[0]] is a synonym of [[zero]]           |
| /c/en/0/n/wp/number     | /r/Synonym     | /c/en/0/n/wp/number              | 0                 | 0                          | synonym        | CN     |                                          |
| /c/en/000               | /r/RelatedTo   | /c/en/112                        | 000               | 112                        | related to     | CN     |                                          |
| /c/en/000               | /r/RelatedTo   | /c/en/911                        | 000               | 911                        | related to     | CN     |                                          |
| /c/en/000               | /r/RelatedTo   | /c/en/999                        | 000               | 999                        | related to     | CN     |                                          |

  

### （2）数据分析

构建 neo4j 数据库需要的字段有三个`node1;label`,  `node2;label`,  `relation;label`，分别可以视作主语、谓语和宾语。

node 节点中的问题：

#### 1. 数据复杂

不同源的数据不同：
```
// 比如 fnc 的数据就不是很全，所以我就直接舍去了
['fn:fe:abundant_entities-fn:HasLexicalUnit-/c/en/chestnut', 'fn:fe:abundant_entities', 'fn:HasLexicalUnit', '/c/en/chestnut', '', '', '', '', 'FNC']
```

#### 2. 关系复杂

node1 是 `back|railway line|train`, node2 是 `car|cars|green truck|is|pick up|pickup truck|small car|truck|vehicle|white car`, 关系是 `a part of|and|are behind|are on back of|are on top of|are on|at front|attached to|attached|attatched to|behind|being pulled by|beside|by|car|closed on|connected on|driving|facing|for|forming|from|has|in front of|in|near|next to|next|of a|of|on a|on back of|on end of|on left of|on side of|on top of|on|or|parked on side of|part of|pulled by|pulling|to be hit by|waiting for`

类似下面这种： ![data_problem_node_content](pics\data_problem_node_content.png)



因此，我们需要想办法解决这个问题。



## 3. 常识知识图谱构建过程

### step1: 下载数据

在目录下新建 `data` 文件夹，从数据集网站上下载 cskg.tsv.gz，并将其解压到 data 文件夹下。

在 data 文件夹下使用 bash 运行如下命令：

```bash
$ wc -l cskg.tsv
6001532
```

可知 cskg 有 6,001,532 条语句。

### step2: 预处理

预处理部分，我做了如下处理：

- 部分 label 名字为空的行舍去了，所以我们获得的关系比原有的关系要少 45660 条。
- 将没有 sentence 的关系的 sentence 设置为 NoneSentence。

运行 `cskg_process_sentence.py`，得到 `cskg_entity.csv` 和 `cskg_relation.csv` 两个文件。

在 data 文件夹下使用 bash 运行如下命令：

```
$ wc -l cskg_entity.csv
2160968
$ wc -l cskg_relation.csv
5955872
```

可知我们获取的节点有 2,160,968 个节点，有 5,955,872 个关系。

### step3：导入 neo4j

参考 https://neo4j.com/docs/operations-manual/current/tutorial/neo4j-admin-import/#_import_a_small_data_set


#### (1) 修改配置文件

将位于 neo4j 安装根目录下的 `conf/neo4j.conf` 文件的 `dbms.default_database` 的值改为 `cskg.db`。

```
 # The name of the default database
 #dbms.default_database=neo4j
 dbms.default_database=cskg.db
```

#### (2) 复制数据

将 **step2** 中获取到的两个 csv 文件放到 neo4j 安装的根目录下的 `import` 文件夹中。

#### (3) 导入数据

在 neo4j 安装根目录下运行命令 `bin/neo4j-admin.bat import --database=cskg.db  --delimiter="\t" --nodes=import/cskg_entity.csv --relationships=import/cskg_relation.csv`，成功后会显示如下结果。

```shell
IMPORT DONE in 39s 420ms.
Imported:
  2160968 nodes
  5955872 relationships
  4321936 properties
```

我们可以看到，这种方式导入数据，只需要一分钟即可。

#### (4) 启动 neo4j

启动 neo4j 检查数据库是否可以正常访问。

运行 `neo4j console` 的命令，打开 `http://localhost:7474/` 检查是否可以正常连接 neo4j 的 cskg.db 数据库。



至此，常识知识图谱 CSKG 已经构建完毕。



> 节点和关系太多，下面这个方法无法快速构建常识知识图谱。
> #### (1) 修改配置文件
>
> 将位于 neo4j 安装根目录下的 `conf/neo4j.conf` 文件的 `dbms.default_database` 的值改为 `cskg.db`。
>
> ```
> # The name of the default database
> #dbms.default_database=neo4j
> dbms.default_database=cskg.db
> ```
>
> #### (2) 启动 neo4j
>
> 启动 neo4j 检查数据库是否可以正常访问。
>
> 运行 `neo4j.bat console` 的命令，打开 `http://localhost:7474/` 检查是否可以正常连接 neo4j 的 cskg.db 数据库
>
> > 如果在 neo4j 启动后报错提示 database 的名称中含有 illegal charactrs，说明版本太高，需要 jvm11及以上，因此建议下载 3.5 版本的 commmunity neo4j。
>
> #### (3) 复制数据
>
> 将 **step2** 中获取到的两个 csv 文件放到 neo4j 安装的根目录下的 `import` 文件夹中。
>
> #### (4) 导入数据
>
> 打开 `http://localhost:7474/` 运行如下命令。参考 https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/
>
> ##### 1. 导入实体
>
> ```CQL
> :auto USING PERIODIC COMMIT 3000
> LOAD CSV FROM "file:///cskg_entity.csv" AS line
> MERGE (:Entity {name: line[0]})
> ```
>
> 上述命令是为了将实体导入至 neo4j 数据库中，用时一秒钟左右。
>
> ##### 2. 创建索引【进行中】
>
> ```cql
> CREATE INDEX ON :Entity(name)
> ```
>
> 实验表明，如果在不建立索引的情况下导入关系，会导致运行之间特别漫长。因此在导入关系之前，我们必须先建立索引。
>
> ##### 3. 导入关系【进行中】
>
> ```cql
> :auto USING PERIODIC COMMIT 3000
> LOAD CSV FROM "file:///cskg_relation.csv" AS line
> MATCH (subject:Entity {name: line[0]})
> MATCH (object:Entity {name: line[2]})
> MERGE (subject)-[:RELATION{name: line[1]}]->(object)
> ```
>
> 上述命令是为了将关系导入至 neo4j 数据库中，用时较久。


# 二、反事实用例判断
## 1. 基于知识图谱的反事实用例判断 【work. 1】（知识图谱可以匹配表示事实，否则反事实）
### (1) 基于关系

比如 antonym 反义词关系。

```
找关系
```

### (2) 基于距离

超过几跳可以认为是反事实，比如两跳。
首先需要构建实体集合和关系集合。

### 问题
可能存在的问题如下：
- 实体集合没有见过给定的实体或者关系怎么办？
  这种情况会比较少，因为我们拥有两百多万个节点和六百万条关系，这些足以建模整个英语体系的常识。
  但是，比如给定一个专业术语，很有可能是找不到的，这就超出了 CSKG 的处理范围。

## 2. 基于自然语言模型的反事实用例判断 【work. 2】（语言模型微调）
根据常识数据集构建常识语言模型。

```
输入：部分事实语句，比如两千句。
输出：模型。
判断：即可。
```

### Bert 模型

#### 1. 数据集构建

从 cskg.tsv 中获取常识的句子。运行`model_sentences.py` 即可生成 `common_sense_sentences.dataset` 文件。

```
$ wc -l .\data\common_sense_sentences.dataset
604768
```

共有 60 万个句子。

#### 2. 输入模型



# 三、反事实用例生成
## 1. 基于规则的替换
   代码位置在 `src/rules-based_genarated.py`
### 1. 属性及量纲替换：人的身高1.8m -> 人的身高180m 人的身高1.8m -> 人的身高1.8cm
   通过字符串正则匹配的方式匹配字符串其中的数字和数字后的量纲，从而进行相应的诸如正负替换，数字扩大缩小替换以及量纲替换
### 2. 远义替换：牛吃草 -> 矩阵吃草

   ```
   核心算法：通过文中使用的相似度算法计算各主语和各宾语之间的相似度，寻找某一主语或宾语相似度最低的词语替换该主语或宾语
   ```

   ​

## 2. 基于知识图谱 【work. 4 & work . 5】（没有提示）
### 1. 基于关系：关系中存在反义词的关系
 运行 `py2neo_antonym.py`, 可以获取如下结果。

   ```
   raw text: [[cosmetic]] is a synonym of [[enhancive]]
   counterfactual:
   ['[[utilitarian]] is a synonym of [[enhancive]]', '[[useful]] is a synonym of [[enhancive]]', '[[unartistic]] is a synonym of [[enhancive]]', '[[unaesthetic]] is a synonym of [[enhancive]]', '[[structural]] is a synonym of [[enhancive]]', '[[inartistic]] is a synonym of [[enhancive]]', '[[inaesthetic]] is a synonym of [[enhancive]]', '[[functional]] is a synonym of [[enhancive]]', '[[disfiguring]] is a synonym of [[enhancive]]', '[[cosmetic]] is a synonym of [[weakening]]', '[[cosmetic]] is a synonym of [[unartistic]]', '[[cosmetic]] is a synonym of [[unaesthetic]]', '[[cosmetic]] is a synonym of [[tempering]]', '[[cosmetic]] is a synonym of [[palliative]]', '[[cosmetic]] is a synonym of [[moderating]]', '[[cosmetic]] is a synonym of [[mitigatory]]', '[[cosmetic]] is a synonym of [[mitigative]]', '[[cosmetic]] is a synonym of [[lenitive]]', '[[cosmetic]] is a synonym of [[inartistic]]', '[[cosmetic]] is a synonym of [[inaesthetic]]', '[[cosmetic]] is a synonym of [[anodyne]]', '[[cosmetic]] is a synonym of [[analgetic]]', '[[cosmetic]] is a synonym of [[analgesic]]', '[[cosmetic]] is a synonym of [[alleviatory]]', '[[cosmetic]] is a synonym of [[alleviative]]']
   ==========
   raw text: [[evergreen]] is related to [[christmas tree]]
   counterfactual:
   ['[[broad-leaved]] is related to [[christmas tree]]', '[[broad-leafed]] is related to [[christmas tree]]', '[[deciduous]] is related to [[christmas tree]]', '[[broadleaf]] is related to [[christmas tree]]', '[[deciduous tree]] is related to [[christmas tree]]', '[[deciduous]] is related to [[christmas tree]]', '[[perdifoil]] is related to [[christmas tree]]']
==========
   raw text: [[hear]] is related to [[noise perception]]
   counterfactual:
   ['[[talk]] is related to [[noise perception]]', '[[speak]] is related to [[noise perception]]', '[[see]] is related to [[noise perception]]', '[[def]] is related to [[noise perception]]', '[[deaf]] is related to [[noise perception]]', '[[smell]] is related to [[noise perception]]', '[[listen]] is related to [[noise perception]]', '[[away]] is related to [[noise perception]]']
==========
   ```


### 2. 基于距离：超过几跳可以生成反事实

   运行 `py2neo_jump_2nd.py`, 大约一分钟左右，可以获取如下结果。

   ```
   origin:          [[cardinal]] is a synonym of [[primal]]
   replace s:       [[ten]] is a synonym of [[primal]]
   replace o:       [[cardinal]] is a synonym of [[roll ball]]
   ----------
   origin:          [[James Bond]] has [[a license to kill]]
   replace s:       [[1000]] has [[a license to kill]]
   replace o:       [[James Bond]] has [[enter house]]
   ----------
   origin:          [["0"]] is [[pronounced zero]]
   replace s:       [[measles]] is [[pronounced zero]]
   replace o:       [["0"]] is [[found inside house]]
   ----------
   origin:          [[1]] can [[equal 1]]
   replace s:       [[drawer]] can [[equal 1]]
   replace o:       [[1]] can [[nearness measurement]]
   ----------
   origin:          [[Internet]] is made of [[tu hermana en bolas]].
   replace s:       [[element]] is made of [[tu hermana en bolas]].
   replace o:       [[Internet]] is made of [[length traveled]].
   ----------
   ```

## 3. 基于自然语言模型
   需要事实的数据集【1000句左右】，最后构建反事实生成语言模型。

# 四、实验

## 1. 判断反事实用例的实验：

### ① 人工标注数据集+自动化测试  

### ② 人工检查获取共识率

## 2. 生成反事实用例的实验：

### ① 根据我们构建的反事实判断模型进行自动化测试

### ② 人工检查获取共识率

# 五、论文撰写

见`paper/README.md` 文件。
