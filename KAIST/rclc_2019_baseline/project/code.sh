#!/usr/bin/env bash
cd /project
pwd

# run python file
export PYTHONPATH=${PYTHONPATH}:`pwd`
python3 -m nltk.downloader punkt stopwords
echo "Dataset(1/3)--------------------------------------------------------------------------"
python3 ./docqa/scripts/run_on_user_documents_eval_final-mod_ph2_.py ./pretrain/cpu
echo "Dataset(2/3)--------------------------------------------------------------------------"
python3 ./ner/DocQA2UltraFine.py
echo "Dataset(3/3)--------------------------------------------------------------------------"
python3 ./ner/open_type/rcc_ultra_fine_main_v2.py release_model -lstm_type single -enhanced_mention -data_setup joint -add_crowd -multitask -mode test -reload_model_name release_model -load
echo "Field---------------------------------------------------------------------------------"
#python3 ./research_field.py
echo "Method--------------------------------------------------------------------------------"
#python2 ./method/tagger.py
