import re
import random,time
from typing import Pattern




def split_word(str):
    pattern = re.compile('\[\[[^\[\]]+\]\]')
    word_list  = pattern.findall(str)
    return word_list 

def random_number_no_repeat(num,whole_num):
    set_1 = set()
    while len(set_1)<num:
        set_1.add(random.randint(0,whole_num))
    return set_1


def construct_words_similarity(subject_list,object_list):
    # 先构建相似度矩阵，除自己的位为1以外其余都为0
    list_num = len(subject_list)
    subject_similarity_matrix = []
    object_similarity_matrix = []
    for row in range(1,list_num):
        temp_list = []
        for col in range(1,list_num):
            if col == row :
                temp_list.append(1)
            else :
                temp_list.append(0)
        subject_similarity_matrix.append(temp_list)
        object_similarity_matrix.append(temp_list)
    
    object_subject_matrix = []
    subject_object_matrix = []
    for row in range(1,list_num):
        temp_list = []
        object_subject_matrix.append(temp_list)
        subject_object_matrix.append(temp_list)
    for num in range(1,list_num):

        object_subject_matrix[num].append(subject_list[num])
        subject_object_matrix[num].append(object_list[num])
    
    for num in range(1,list_num):
        a_row_length = len(object_subject_matrix[num])
        for low in range(1,a_row_length):
            for middle in range(low,a_row_length):
                subject_similarity_matrix[low][middle] = 0.5
    
    for num in range(1,list_num):
        a_row_length = len(subject_object_matrix[num])
        for low in range(1,a_row_length):
            for middle in range(low,a_row_length):
                object_similarity_matrix[low][middle] = 0.5
    epoch = 0
    while epoch < 5 :
        similar_value = 1/(epoch+2)**2
        for row in range(1,list_num):
            similar_subject_list = []
            for col in range(1,list_num):
                if subject_object_matrix[row][col] == 2*similar_value:
                    similar_subject_list.append(col)
            similar_object_list = []
            for a_subject_index in similar_subject_list:
                for a_object in object_subject_matrix[a_subject_index]:
                    similar_object_list.append(a_object)
            for similar_subject_col in range(1,list_num):
                if subject_object_matrix[row][similar_subject_col] == 0:
                    subject_object_matrix[row][similar_subject_col] = similar_subject_list

    # for num in range(1,list_num):
    return subject_similarity_matrix,object_similarity_matrix
        

    




# 先读取所有的单词，将其按照对应的列表存储，即分别为 主语列表和宾语列表 ，这称为构建步骤
# 之后生成阶段时，由两个函数分别生成量纲修改的反事实和随机替换的反事实
def dimensional_replacement(str_list,random_list):
    result_list = []
    pattern_1 = '(\[\[[^\[\]0]*)(0+)([^\[\]]*\]\])'
    pattern_2 = '(\[\[[^\[\]\d-]*)([1-9]+[.]*[0-9]*)([^\[\]]*\]\])'
    pattern_3 = '(\[\[[^\[\]\d-]*)(-[0-9]+[.]*[0-9]*)([^\[\]]*\]\])'
    for index in random_list:
        str = str_list[index]
        # new_str = str.replace("0","10000")
        # 将0变为一个不为0的数
        new_str = re.sub(pattern_1,lambda m:m.group(1)+"1000000"+m.group(3),str)
        if new_str != str:
            result_list.append(new_str)
        # 将正数变为负数
        new_str_2 = re.sub(pattern_2,lambda m:m.group(1)+"-"+m.group(2)+m.group(3),str)
        if new_str_2 != str:
            result_list.append(new_str_2)
        # 将负数变为正数
        new_str_3 = re.sub(pattern_3,lambda m:m.group(1)+m.group(2).split("-")[1]+m.group(3),str)
        if new_str_3 !=str:
            result_list.append(new_str_3)
    return result_list

        
        


# 获得主语和宾语列表，用于替换
def construct_two_list(file_path):
    string_list = []
    subject_list = []
    object_list = []
    for line  in open(file_path):
        string_list.append(line)
        word_list = split_word(line)
        if len(word_list) == 2:
            subject_list.append(word_list[0])
            object_list.append(word_list[1])
    return string_list,subject_list,object_list

def construct_random_str_list(str_list,random_list):
    result_list = []
    for num in random_list:
        result_list.append(str_list[num])
    return result_list


def random_replacement(str_list,subject_list,object_list):
    #假定输入1000个原有字符串，生成2000个反事实字符串
    #将随机的1000个主语替换到原str中，以及随机的1000个宾语替换到原str中
    result_list = []
    whole_num = 200000
    nums = random_number_no_repeat(10000,whole_num)
    index = 0
    for num in nums:
        a_str = str_list[index]
        word_list = split_word(a_str)
        substring_0 = a_str.split(word_list[0])[1]
        new_subject_string = subject_list[num]+""+substring_0
        result_list.append(new_subject_string)
        substring_1 = a_str.split(word_list[1])[0]
        new_object_string = substring_1+""+object_list[num]
        result_list.append(new_object_string)
        index+=1
    return result_list



def write_list_to_file(result_list,file_name):
    f = open(file_name,"w")
    for line in result_list:
        f.write(line+"\n")
    f.close()


input_path = "common_sense_sentences.dataset"
str_list_path = "string_list_for_ouptut_sentences.dataset"
output_path = "output_sentences.dataset"
string_list,subject_list,object_list = construct_two_list(input_path)
random_list = random_number_no_repeat(10000,200000)
random_str_list = construct_random_str_list(string_list,random_list)
result_list = random_replacement(random_str_list,subject_list,object_list)
write_list_to_file(result_list,output_path)
write_list_to_file(random_str_list,str_list_path)




# input_path = "common_sense_sentences.dataset"
# output_path = "output_sentences_2.dataset"
# string_list,subject_list,object_list = construct_two_list(input_path)
# random_list = random_number_no_repeat(10000,200000)
# result_list = dimensional_replacement(string_list,random_list)
# write_list_to_file(result_list,output_path)




    
    



