#!/usr/bin/env python
# coding: utf-8



import json
import re
import time
from config import params



# return a list of the indexes where ch appears in s
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


# Open the publication whose id is paper_id
def read_paper(paper_id):
    with open(params['PROCESSED_DOCPATH']+ paper_id + ".txt", "r", encoding='utf-8') as f:
        paper = f.readlines()
    return paper

# Ignore non-space and non-word characters
def equal(a, b):
    return [c for c in a if c.isalpha()] == [c for c in b if c.isalpha()]


# Given a paper like bla bla bla. sentence with the dataset name. bla bla bla
# We are looking for the dots '.' that are surrounding the sentence with the dataset name
# return sentence with the dataset name
def get_context(paper, mention):
    idx = paper.find(mention)
    if idx != -1:
        #Let's extract the full sentence so let's get the '.' that appears before and after the mention
        list_dots = find(paper, '.')
        for i, dot in enumerate(list_dots):
            if dot > idx: #If we found the final dot of the sentence with the dataset name
                #we also check that the context is not just the mention. If we find that case, we get the next line as context
                if i == 0 and not equal(processed_paper[list_dots[i-1]+1:dot], mention): #it is in the first line list_dots[i] == dot
                    return processed_paper[0:dot]
                elif not equal(processed_paper[list_dots[i-1]+1:dot], mention):
                    return processed_paper[list_dots[i-1]+1:dot] #from end of previous sentence to the end of the sentence with the mention
    return ""


# Creates the input of one candidate answer for ultra fine
def format_to_ultra_fine(text, substring, annot_id, paper_id):
    left_context = str(text[0:text.find(substring)].split())
    right_context = str(text[text.find(substring)+len(substring):].split())
    if left_context == "[]" and right_context == "[]":
        #print(paper_id, substring, annot_id)
        return ""
    elif substring == "":
        return ""
    else:
        output = '{"y_str": [], "annot_id": "(' + paper_id + "," + substring + "," + annot_id + ')", "mention_span": "' + substring + '", "right_context_token": ' + right_context + ', "left_context_token": ' + left_context + "}\n"
        return output.replace('\'', '\"' )

if __name__ == "__main__":
    start_time = time.time() 
    # main
    docqa_output_file = params['RESEARCH_DATA_NO_ID_OUTPUT_PATH']
    with open(docqa_output_file) as f:
        docqa_output = json.load(f)

    ultra_fine_output_file = params['INPUT_ULTRAFINE_PATH']

    with open(ultra_fine_output_file, "w") as f: 
        for docqa in docqa_output:
            paper_id = str(docqa["publication_id"])
            paper = read_paper(paper_id)
            processed_paper = re.sub('[^A-Za-z0-9.]+', ' ', " ".join(paper)) #Remove ' and " and other special char
            processed_mention = re.sub('[^A-Za-z0-9.]+', ' ', docqa['mention']) #Remove ' and " and other special char
            context = get_context(processed_paper, processed_mention)
            if processed_mention != "":
                f.write(format_to_ultra_fine(context, processed_mention, str(docqa['score']), paper_id)) #write in the json file for ultra fine entity
    print("--- %s seconds ---" %(time.time() - start_time))





