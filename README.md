# citation_processing

- **create_data_sets.py** -- creates data_sets.json
- **create_citations.py**  -- creates data_set_citations.json and updates publications.json
- **extract_text_from_pdf.py** -- converts PDFs in ~/Zotero/storage to text files in data/input/files/text/

- cp data/input/files/text/* project/data/dev/input/files/text/
- cp data_set_citations.json publications.json project/data/dev/
- cd project
- python to_conll.py --data_folder_path data      # creates project/data/dev/ner-conll/ and project/data/dev/linking-conll/
- cd ../
- mkdir project/data.new/
- python project/ner_retraining/create_splits.py # creates project/data.new/{dev,test,train}_concat.conll project/data.new/{dev,test,train}_papers.txt

- point project/ner_model/allennlp-ner-config.json to {dev,test,train}_concat.conll
- allennlp train project/ner_model/allennlp-ner-config1.json -s project/model --include-package ner_rcc

- create project/data/publications_test.json -- contains publications that we want to test NER model with

- python to_conll_test.py  # creats project/data/ner-conll/*conll from project/data/input/files/text/ listed in project/data/publications_test.json

- python project/ner_retraining/generate_ner_output.py --conll_path project/data/ner-conll/ --output_path project/data/output/ner_output.json --model_path project/model/        # creates data/output/ner_output.json
