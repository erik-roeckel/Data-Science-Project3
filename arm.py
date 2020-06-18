import sys
import csv
import math
import string
from itertools import combinations
from itertools import permutations

input_data = sys.argv[1]
output_data = sys.argv[2]
min_supp_percentage = sys.argv[3]
min_confidence = sys.argv[4]

support_counts = {}
item_list = []

#read data from csv file into list, remove transaction ID
def read_input_data(input_data):
    with open(input_data, 'r') as csv_input:
        reader = csv.reader(csv_input, delimiter=',')
        for row in reader:
            row_data = row
            row_data.pop(0)
            item_list.append(row_data)

#filter out any punctuation that may be in csv data
def filter_data():
    item_data = [''.join(x) for x in item_list]
    filter_data = [''.join(char for char in s if char not in string.punctuation) for s in item_data]
    return filter_data

# create string of single items so we can generate all possible permutations
def create_item_string():
    item_string = ""
    exists = ""
    for items in sorted(filtered_data):
        for item in items:
            if item not in exists:
                exists += item
                item_string += item
    return item_string

# function to get the candidate frequent itemsets, generates all combinations of input values
# returns a list of all possible combinations of items
def get_CFI():
    cfi = []
    for i in range(len(item_string)):
        if i is not 0:
            for p in combinations(item_string, i):
                p= tuple(sorted(p))
                cfi.append(p)
    return cfi

# function to calculate the verified frequent itemsets
# returns a dictionary that stores any tuple (itemset) as the key with a support % greater than min support percentage as the value
def get_VFI():
    VFI = {}
    for item_tuple in CFI:
        supp_count = 0
        temp = str(item_tuple)
        for item in filtered_data:
            temp_tuple= ""
            for char in item_tuple:
                if char in item:
                    temp_tuple += char
            if len(temp_tuple) == len(item_tuple):
                supp_count += 1
        temp_supp_percentage = supp_count/len(filtered_data)
        if temp_supp_percentage >= float(min_supp_percentage):
            support_counts[item_tuple] = supp_count
            VFI[item_tuple] = temp_supp_percentage
    return VFI

# function to calculate any associative relations, based on VFI calculated in pervious function
def get_all_associative_relations():
    all_assoc_relations = []
    first_partition = []
    second_partition = []
    for item_set in VFI:
        if len(item_set) > 1:
            curr_size = len(item_set)
            for perm in permutations(item_set):
                left_size = curr_size//2
                if curr_size == 2:
                    first_partition.append(perm[0])
                    second_partition.append(perm[1])
                else:
                    first_partition.append(perm[0:left_size])
                    second_partition.append(perm[left_size:curr_size])

    for i in range(len(first_partition)):
        left_string = str(sorted(first_partition[i]))
        right_string = str(sorted(second_partition[i]))
        assoc = left_string +"=>" + right_string
        all_assoc_relations.append(assoc)
    
    for i in range(len(second_partition)):
        left_string = str(sorted(second_partition[i]))
        right_string = str(sorted(first_partition[i]))
        assoc = left_string + "=>" + right_string
        if assoc not in all_assoc_relations:
            all_assoc_relations.append(assoc)
    return all_assoc_relations

# from the list of all possible associative relations get the ones that are in VFI
# and have confidence greater than or equal to min confidence
def get_relevant_relations():
    relevant_relations = []
    already_exists = []
    for relation_string in all_associative_relations:
        relation = relation_string.split("=>")
        left_filtered = [''.join(char for char in relation[0] if char not in string.punctuation)]
        right_filtered = [''.join(char for char in relation[1] if char not in string.punctuation)]
        left_count = 0
        union_count = 0
        for r in support_counts.keys():
            full_set = 0
            split_tuple = left_filtered[0].split(" ")
            for char in split_tuple:
                if char in r:
                    full_set += 1
            if full_set == len(r):
                left_count = support_counts[r]
        
        for i in support_counts.keys():
            full_set = 0
            for char in left_filtered[0].split(" ") + right_filtered[0].split(" "):
                if char in i:
                    full_set += 1
                if full_set == len(i):
                    union_count = support_counts[i]
        if left_count != 0:
            confidence = union_count/left_count
        if (float(confidence) >= float(min_confidence)):
            already_exists.append([union_count/len(filtered_data), confidence, left_filtered[0].split(" "), right_filtered[0].split(" ")])
            for sets in already_exists:
                if sets not in relevant_relations:
                    relevant_relations.append([union_count/len(filtered_data), confidence, left_filtered[0].split(" "), right_filtered[0].split(" ")])
        
    return relevant_relations

# write to csv any verified frequent itemsets found from input data
def write_frequent_itemsets():
    for item_tuple in VFI:
        support = VFI[item_tuple]
        verified_tuple = ','.join(item_tuple)
        file_writer.writerow(["S,%.4f,%s"%(support, verified_tuple)])

# write to csv any associative relations found from list of verified frequent itemsets
def write_assoc_relations():
    for relation in relevant_associative_relations:
        support = float(relation[0])
        confidence = float(relation[1])
        left_side = ','.join(relation[2])
        right_side = ','.join(relation[3])
        arrow = "'=>'"
        file_writer.writerow(["R,%.4f,%.4f,%s,%s,%s" %(support, confidence, left_side, arrow, right_side)])


read_input_data(input_data)
filtered_data = filter_data()
item_string = create_item_string()
CFI = get_CFI()
VFI = get_VFI()
all_associative_relations = get_all_associative_relations()
relevant_associative_relations = get_relevant_relations()
csv_output = open(output_data, mode = 'w', newline='')
file_writer = csv.writer(csv_output, delimiter=" ")
write_frequent_itemsets()
write_assoc_relations()

print("\nResults written to " + output_data + "\n")


