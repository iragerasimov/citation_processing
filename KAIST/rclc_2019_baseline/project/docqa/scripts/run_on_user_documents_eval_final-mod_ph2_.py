import argparse
import json
import pickle
import re
import time
from itertools import combinations
from os.path import isfile

import numpy as np
import tensorflow as tf
from tqdm import tqdm

from docqa.data_processing.document_splitter import MergeParagraphs, TopTfIdf, ShallowOpenWebRanker, PreserveParagraphs
from docqa.data_processing.qa_training_data import ParagraphAndQuestion, ParagraphAndQuestionSpec
from docqa.data_processing.text_utils import NltkAndPunctTokenizer, NltkPlusStopWords
from docqa.doc_qa_models import ParagraphQuestionModel
from docqa.model_dir import ModelDir
from docqa.utils import flatten_iterable

from config import params


#
#
#
#
#

def pre_processing(txt):
    
    '''
    doctext = ''
    paralist = txt.split('.\n')
    for para in paralist:
        doctext += re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', para.replace('-\n','').replace('\n',' ').strip())
        doctext += '.\n'
    '''
    
    txt_processed = txt.replace('-\n','').replace('.\n','__PAR__').replace('\n',' ').replace('__PAR__','.\n')
    filtered_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', txt_processed)
    return filtered_string

'''
-Name: tokenizing_doc_and_save
-Desc: Tokenizing a publication and then save it
-Input: 
    docpath(string) : Path to publications
    savepath(string) : Path to save tokenized publications
    docid(int) : id of publication
    tokenizer: NLTK tokenzier
-Output:
    None
'''
def tokenizing_doc_and_save(docpath, savepath, docid, tokenizer, process_path):
    docpath = [docpath + str(docid) + '.txt']
    list_documents = []
    
    for doc in docpath:
        if not isfile(doc):
            raise ValueError(doc + " does not exist")
        with open(doc, "r", encoding = 'utf-8') as f:
            txt = f.read()
        processed_txt = pre_processing(txt)
        list_documents.append(processed_txt)
    
    with open(process_path + str(docid) + '.txt', mode = 'w', encoding = 'utf-8') as fw:
        fw.write(processed_txt)
    
    list_documents = [re.split("\s*\n\s*", doc) for doc in list_documents]
    list_documents = [[tokenizer.tokenize_paragraph(p) for p in doc] for doc in list_documents]
    splitter = MergeParagraphs(400)
    list_documents = [splitter.split(doc) for doc in list_documents]
    
    with open (savepath + str(docid) + '.pickle', mode = 'wb') as f:
        pickle.dump(list_documents, f)
        
'''
-Name: find_voc
-Desc: Find vocabulary in a question and publications
-Input: 
    jsonfile(json list) :  Publications.json
    question(list) :  List of tokens of a question
    docpath(string) :  Path to publications
    model: Docqa Model
-Output:
    set_voc(set) : Set of vocabulary
'''
        
def find_voc(jsonfile, question, docpath, model, question_v):
    set_voc = set(question + question_v)
    for citation in tqdm(jsonfile):
        docid = citation["publication_id"]
        set_voc = find_voc_in_doc(docpath, docid, model, set_voc, question)
    return set_voc

'''
-Name: find_voc_in_doc
-Desc: Find new vocabularies in a publication and update vocabulary set
-Input: 
    docpath(string) : Path to publications
    dodid(int) : id of publication
    model: Docqa Model
    set_voc(set) : Set of vocabulary
    question(list) : List of tokens of a question
-Output:
    set_voc(set) : Set of vocabulary
'''

def find_voc_in_doc(docpath, docid, model, set_voc, question):
    
    with open(docpath + str(docid) + '.pickle', mode = 'rb') as f:
        list_documents = pickle.load(f)
    if len(list_documents) == 1:
        selector = TopTfIdf(NltkPlusStopWords(True), n_to_select=3)
        context = selector.prune(question, list_documents[0])
    else:
        selector = ShallowOpenWebRanker(n_to_select=3)
        context = selector.prune(question, flatten_iterable(list_documents))
    if model.preprocessor is not None:
        context = [model.preprocessor.encode_text(question, x) for x in context]
    else:
        context = [flatten_iterable(x.text) for x in context]
    for txt in context:
        set_voc.update(txt)
    return set_voc

'''
-Name: model_handler_nodataid
-Desc: Extract dataset mention, and confidence score
-Input: 
    dict_docqa_result(dictionary) : Key is publication id and values are candidates(dataset), confidence scores
    question(list) : List of tokens of a question
    docpath_p(string) : Path to tokenized publications
    model: Docqa Model
    model_dir: Pretrained model
    set_voc(set) : Set of vocabulary
    jsonfile(json list) : Publications.json
    question_vocablist(list): Vocab of queries
    tokenizer(NltkAndPunctTokenizer):tokenizer
-Output:
    dict_docqa_result(dictionary): Key is publication id and values are candidates(dataset), confidence scores
'''

def model_handler_nodataid(dict_docqa_result, question, docpath_p, model,model_dir, set_voc, jsonfile, question_vocablist, tokenizer):
    
    num_can_in_para = params['DATA_NUM_CANDIATA_IN_PARAGRAPH'] #number of candidates in one paragraph
    num_para = params['DATA_NUM_PARAGRAPH'] #number of paragraphs in one publication
    sim_thre = params['SIM_THRE'] #threshold for sim score
    
    model.set_input_spec(ParagraphAndQuestionSpec(batch_size=None), set_voc)
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))    
    with sess.as_default():
        best_spans, conf = model.get_prediction().get_best_span(8)
    
    model_dir.restore_checkpoint(sess)    
    for citation in tqdm(jsonfile):
        docid = citation["publication_id"]
        
        with open(docpath_p + str(docid) + '.pickle', mode = 'rb') as f:
            documents = pickle.load(f)
        
        if len(documents) == 1:
            selector = TopTfIdf(NltkPlusStopWords(True), n_to_select=num_para)
            context = selector.prune(question, documents[0])
        else:
            selector = ShallowOpenWebRanker(n_to_select=num_para)
            context = selector.prune(question, flatten_iterable(documents))
        if model.preprocessor is not None:
            context = [model.preprocessor.encode_text(question, x) for x in context]
        else:
            context = [flatten_iterable(x.text) for x in context]    
        
        ans_can_list = []
        ans_confi_list = []
        ans_result_datasetid_list = []
              
        for idx in range(0, num_can_in_para):
            query_para_list = query_generator(question_vocablist, context, tokenizer)
            data = [ParagraphAndQuestion(x, query_para_list[idx2], None, "user-question%d"%idx2) for idx2, x in enumerate(context)]
            encoded = model.encode(data, is_train=False)  # batch of `ContextAndQuestion` -> feed_dict
            
            best_spans_, conf_ = sess.run([best_spans, conf], feed_dict=encoded)  # feed_dict -> predictions

            for i in range(len(conf_)):
                cand = " ".join(context[i][best_spans_[i][0]:best_spans_[i][1]+1])
                ans_can_list.append(cand)
                can_score = norm_0_to_1(float(conf_[i]))
                ans_confi_list.append(can_score)

                context[i] = context[i][:best_spans_[i][0]] + context[i][best_spans_[i][1]+1:]
                
        dict_docqa_result[docid]["ans_can"] += ans_can_list
        dict_docqa_result[docid]["ans_confi"] += ans_confi_list
        
    return dict_docqa_result

'''
-Name: query_generator
-Desc: Extract dataset mention, and confidence score
-Input: 
    question_vocablist(list) : List of tokens of a question
    context : doc
    tokenizier(NltkAndPunctTokenizer):tokenizer
-Output:
    n_p(list): list of question for each paragraph
'''

def query_generator(question_vocablist, context, tokenizer):
    n_p = []
    for idx, para in enumerate(context):
        n_ = []
        for word in para:
            for n in question_vocablist:
                if n in word:
                    n_.append(n)
        n_ = list(set(n_))
        n_.sort()
        if len(n_) > 0:
            qm = ', '.join(n_)
        else:
            qm = 'survey, dataset, data'
        qm = 'what ' + qm + ' ?'
        #qm = 'what ' + qm + '?'
        n_p.append(tokenizer.tokenize_paragraph_flat(qm))
    return n_p

'''
-Name: select_best_answers_q2
-Desc: Select k, top candidates(methods) with thre threshold
-Input: 
    dict_docqa_result(dictionary) : Key is publication id and values are candidates(method) and confidence scores
    k(int) : Top k candidates(dataset) for each publication
    thre(float) : Threshold for confidence score
-Output:
    dict_docqa_result_tuple(dictionary) :  Sorted dictionary with confidence score. Key is publication id and value is tuple that consists of a candidate(methods) and a confidence score
'''

def select_best_answers_q2(dict_docqa_result,k, thre):
    
    dict_docqa_result_tuple = {}
    
    for docid in dict_docqa_result:
        dict_docqa_result_tuple[docid] = []
        
        for idx, can in enumerate(dict_docqa_result[docid]["ans_can"]):
            
            if (dict_docqa_result[docid]["ans_confi"][idx] > thre):
                dict_docqa_result_tuple[docid].append((can, dict_docqa_result[docid]["ans_confi"][idx]))
                
    for key in dict_docqa_result_tuple:
        dict_docqa_result_tuple[key].sort(key=lambda pair: pair[1], reverse=True) #sort by confidence score
        dict_docqa_result_tuple[key] = dict_docqa_result_tuple[key][:k]       
    return dict_docqa_result_tuple

'''
-Name: norm_0_to_1
-Desc: Normalize confidence score
-Input: 
    confi(float) : Confidence score. Max is 20, and min is -20
-Output:
    (confi + 20) / 40 : Normalized confidence score. Max is 1, and min is 0
'''

def norm_0_to_1(confi):
    return (confi + 20) / 40

'''
-Name: create_json_list_nodataid
-Desc: create json list
-Input: 
    dict_tuple_result_without_dataid(dictionary): Key is publication id and values are candidates(dataset), confidence scores
-Output:
    list_arg_withoutid(list) : json list
'''

def create_json_list_nodataid(dict_tuple_result_without_dataid):
    list_arg_withoutid = []
    
    for tuple_without in dict_tuple_result_without_dataid:
        for datam in dict_tuple_result_without_dataid[tuple_without]:
            json_list_nodataid = {"publication_id" : int(tuple_without), "score" : float(datam[1]), "mention":datam[0]}
            list_arg_withoutid.append(json_list_nodataid)
    
    return list_arg_withoutid
        
        
def queryvocab(path):
    with open(path, mode = 'rb') as f:
        vocablist = pickle.load(f)
    return vocablist        
        
'''
-Name: main
-Desc: main function
-Input: 
    datajsonpath(string) : Path to data_sets.json
    model_pretrain(string): Path to pretrained model
-Output:
    None
'''

def main(model_pretrain):
    #Constants
    topk_noid = params['TOP_K_DATA_WITHOUTID'] # Number of dataset for each publication in data_set_mentions.json
    thre = params['THRE_DATA'] # Threshold for confidence score of dataset
    list_question_str = [params['QUESTION_DATA']]
    jsonpath = params['PUBLICATION_JSONPATH']
    docpath = params['PUBLICATION_DOCPATH']
    tokenizedpath = params['TOKENIZED_DOCPATH']
    datasetquestionvocabpath = params['DATASET_QUESTION_VOCAB_PATH']
    process_path = params['PROCESSED_DOCPATH']
    
    outputpath = params['RESEARCH_DATA_NO_ID_OUTPUT_PATH']
    
    #Variables
    dict_docqa_result = {}
    list_arg_withoutid = []
    
    #Publications
    with open(jsonpath, mode = 'r') as f:
        jsonfile = json.load(f)
    
    #Model init
    tokenizer = NltkAndPunctTokenizer()
    model_dir = ModelDir(model_pretrain)
    model = model_dir.get_model()
    model.char_embed.layer.map_layer.keep_probs = 1
    #print("Tokenizing...")
    #Preparing variables
    
    for citation in tqdm(jsonfile):
        docid = citation["publication_id"]
        tokenizing_doc_and_save(docpath, tokenizedpath, docid, tokenizer, process_path)
        dict_docqa_result[docid] = {}
        dict_docqa_result[docid]["ans_can"] = []
        dict_docqa_result[docid]["ans_confi"] = []
        
    #print("Dataset...")
    #Dataset ---------------------
    #For multiple questions
    
    paracan = [4]
    for paranum_ in paracan:
        for question_str in list_question_str:
            question = tokenizer.tokenize_paragraph_flat(question_str)
            question_vocablist = queryvocab(datasetquestionvocabpath)
            question_v = tokenizer.tokenize_paragraph_flat(' '.join(question_vocablist))
            set_voc = find_voc(jsonfile, question, tokenizedpath, model, question_v) #Find vocabulary of question and publications
            dict_docqa_result = model_handler_nodataid(dict_docqa_result, question, tokenizedpath, model,model_dir, set_voc, jsonfile, question_vocablist, tokenizer)
            #tf.reset_default_graph()
        
        
        dict_tuple_result=select_best_answers_q2(dict_docqa_result,topk_noid, thre)
        
        
        list_arg_withoutid = create_json_list_nodataid(dict_tuple_result)
        with open(outputpath, mode = 'w') as f:
            json.dump(list_arg_withoutid, f)
    
if __name__ == "__main__":
    #print("Dataset")
    start_time = time.time() 
    #Arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("model_pretrain", help="Model directory")
    args = parser.parse_args()
    
    main(args.model_pretrain)
    print("--- %s seconds ---" %(time.time() - start_time))
    