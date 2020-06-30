# config.py
params = {
    'DATA_NUM_CANDIATA_IN_PARAGRAPH' : 3, #number of candidates in one paragraph
    'DATA_NUM_PARAGRAPH' : 10, #number of paragraphs in one publication
    'SIM_THRE' : 0.8, #threshold for sim score
    'TOP_K_DATA_WITHOUTID' : 10, # Number of dataset for each publication in data_set_mentions.json
    #'THRE_DATA' : 0.1, # Threshold for confidence score of dataset
    'THRE_DATA' : -9999.0,
    'QUESTION_DATA' : 'Data, survey, statistics, analysis, cohort, census, database, collection',
    'WIKIPEDIA_ARTICLES_PATH' : '/home/haritz/rcc//FinalVersion/rcc_final_version_phase2/rclc/project/wikipedia/research_fields_wiki_data/',
    'SAGE_RESEARCH_FIELDS_CSV': '/home/haritz/rcc//FinalVersion/rcc_final_version_phase2/rclc/project/sage_research_fields.csv',
    'PUBLICATION_JSONPATH' : "/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/data/input/publications.json",
    'PUBLICATION_DOCPATH' : '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/data/input/files/text/',
    'TOKENIZED_DOCPATH' : '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/tokenized/',
    'PROCESSED_DOCPATH' : '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/processed/',
    'RESEARCH_FIELDS_OUTPUT_PATH': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/data/output/research_fields.json',
    'RESEARCH_DATA_NO_ID_OUTPUT_PATH': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/intermediate_results/data_set_mentions.json',
    'RESEARCH_METHOD_OUTPUT_PATH': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/data/output/methods.json',
    'DATASET_QUESTION_VOCAB_PATH' : '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/queryselection/querylist.pickle',
    'DOCQA_CANDIDATE_ANSWER_CLASSIFIER_PATH' : '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/ner/release/answer_classifier_50_hidden_layer_1_epoch.pth',
    'INPUT_ULTRAFINE_PATH': '/home/haritz/rcc//FinalVersion/rcc_final_version_phase2/rclc/project/ner/release/crowd/inputUltraFine.json',
    'OUTPUT_DOCQA_PATH': '/home/haritz/rcc//FinalVersion/rcc_final_version_phase2/rclc/data/output/data_set_mentions.json',
    'FILE_ROOT': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/ner/release/',
    'GLOVE_VEC': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/wordvector/glove/',
    'EXP_ROOT': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/ner/models/',
    #'THRE_CLASSIFIER' : 0.2,
    'THRE_CLASSIFIER' : 0.1,
    'METHOD_MODEL': '/home/haritz/rcc/FinalVersion/rcc_final_version_phase2/rclc/project/bi-lstm-crf/',
}