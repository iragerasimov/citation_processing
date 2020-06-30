#!/usr/bin/env python3
import datetime
import gc
import logging
import pickle
import os
import sys
import time, json
from tqdm import tqdm

import torch
from torch import nn
import torch.nn.functional as F
from torch import optim
import numpy as np
import torch.utils.data as data_utils
from torch.autograd import Variable
from torch import optim
from tensorboardX import SummaryWriter

import ner.open_type.data_utils as data_utils
import ner.open_type.models as models
from ner.open_type.data_utils import to_torch
from ner.open_type.eval_metric import mrr
from ner.open_type.model_utils import get_pred_str, get_gold_pred_str, get_eval_string, get_output_index

import ner.open_type.config_parser as config_parser
import ner.open_type.resources.constant as constant
import ner.open_type.eval_metric as eval_metric
from config import params

#sys.path.insert(0, './resources')
#import config_parser, constant, eval_metric


class TensorboardWriter:
  """
  Wraps a pair of ``SummaryWriter`` instances but is a no-op if they're ``None``.
  Allows Tensorboard logging without always checking for Nones first.
  """

  def __init__(self, train_log: SummaryWriter = None, validation_log: SummaryWriter = None) -> None:
    self._train_log = train_log
    self._validation_log = validation_log

  def add_train_scalar(self, name: str, value: float, global_step: int) -> None:
    if self._train_log is not None:
      self._train_log.add_scalar(name, value, global_step)

  def add_validation_scalar(self, name: str, value: float, global_step: int) -> None:
    if self._validation_log is not None:
      self._validation_log.add_scalar(name, value, global_step)


def get_data_gen(dataname, mode, args, vocab_set, goal):
  dataset = data_utils.TypeDataset(params['INPUT_ULTRAFINE_PATH'], lstm_type=args.lstm_type,
                                     goal=goal, vocab=vocab_set)
  if mode == 'train':
    data_gen = dataset.get_batch(args.batch_size, args.num_epoch, forever=False, eval_data=False,
                                 simple_mention=not args.enhanced_mention)
  elif mode == 'dev':
    data_gen = dataset.get_batch(args.eval_batch_size, 1, forever=True, eval_data=True,
                                 simple_mention=not args.enhanced_mention)
  else:
    data_gen = dataset.get_batch(args.eval_batch_size, 1, forever=False, eval_data=True,
                                 simple_mention=not args.enhanced_mention)
  return data_gen


def get_datasets(data_lists, args):
  data_gen_list = []
  vocab_set = data_utils.get_vocab()
  for dataname, mode, goal in data_lists:
    data_gen_list.append(get_data_gen(dataname, mode, args, vocab_set, goal))
  return data_gen_list


def load_model(reload_model_name, save_dir, model_id, model, optimizer=None):
  if reload_model_name:
    model_file_name = '{0:s}/{1:s}.pt'.format(save_dir, reload_model_name)
  else:
    model_file_name = '{0:s}/{1:s}.pt'.format(save_dir, model_id)
  checkpoint = torch.load(model_file_name, map_location='cpu')
  model.load_state_dict(checkpoint['state_dict'])
  if optimizer:
    optimizer.load_state_dict(checkpoint['optimizer'])
  else:
    total_params = 0
    # Log params
    for k in checkpoint['state_dict']:
      elem = checkpoint['state_dict'][k]
      param_s = 1
      for size_dim in elem.size():
        param_s = size_dim * param_s
      print(k, elem.size())
      total_params += param_s
    param_str = ('Number of total parameters..{0:d}'.format(total_params))
    logging.info(param_str)
    print(param_str)
  logging.info("Loading old file from {0:s}".format(model_file_name))
  print('Loading model from ... {0:s}'.format(model_file_name))


    
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.l1 = nn.Linear(10332, 50)
        self.l2 = nn.Linear(50, 2)

    def forward(self, x):
        x = x.view(x.shape[0], -1)
        x = F.relu(self.l1(x))
        x = F.dropout(x, p = 0.5, training=self.training)
        x = F.log_softmax(self.l2(x), dim=1)
        return x

    # Load the answer classifier
def load_checkpoint(filepath):
    checkpoint = torch.load(filepath)
    model = Net()
    model.load_state_dict(checkpoint['state_dict'])
    return model

def eval(model, test_loader):
    scores = []
    for (cnt, data) in enumerate(test_loader):
        data = Variable(data, volatile=True).float()
        output = model(data)
        [a] = torch.exp(output).detach().numpy()
        scores.append(a)
    return scores

# return a list of the indexes where ch appears in s
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def process_annot_id(annot_id):
    comma = find(annot_id, ",")
    paper_id = annot_id[1:comma[0]]
    mention = annot_id[comma[0]+1:comma[1]]
    score = annot_id[comma[1]+1:len(annot_id)-1] #score of the candidate answer
    return (paper_id, mention, score)

def _test(args):
  assert args.load
  test_fname = args.eval_data
  data_gens = get_datasets([(test_fname, 'test', args.goal)], args)
  model = models.Model(args, constant.ANSWER_NUM_DICT[args.goal])
  model.eval()
  load_model(args.reload_model_name, constant.EXP_ROOT, args.model_id, model)
  model_checkpoint_file = params['DOCQA_CANDIDATE_ANSWER_CLASSIFIER_PATH']
  answer_classifier = load_checkpoint(model_checkpoint_file)
  answer_classifier.eval()  
  with open(params['OUTPUT_DOCQA_PATH'], "w+") as f:
    json_answer_list = []
    for name, dataset in [(test_fname, data_gens[0])]:
       print('Processing... ' + name)
       total_gold_pred = []
       total_probs = []
       total_ys = []
       total_annot_ids = []
       for batch_num, batch in tqdm(enumerate(dataset)):
         eval_batch, annot_ids = to_torch(batch)
         loss, output_logits = model(eval_batch, args.goal)
         output_index = get_output_index(output_logits)
         output_prob = model.sigmoid_fn(output_logits).data.cpu().clone().numpy()
         y = eval_batch['y'].data.cpu().clone().numpy()
         gold_pred = get_gold_pred_str(output_index, y, args.goal)
         total_probs.extend(output_prob)
         total_ys.extend(y)
         total_gold_pred.extend(gold_pred)
         total_annot_ids.extend(annot_ids)
         # classify the candidate answers
         for (i, types_prob) in enumerate(output_prob):
            (paper_id, mention, score_docqa) = process_annot_id(annot_ids[i])
            tensor_x = torch.from_numpy(np.append(types_prob, float(score_docqa)))
            tensor_x = tensor_x.view(1,tensor_x.shape[0])
            data = Variable(tensor_x, volatile=True).float()
            output = answer_classifier(data)
            [score] = torch.exp(output).detach().numpy()
            if score[1] >= params['THRE_CLASSIFIER']:
               answer = {"publication_id": int(paper_id) , "mention":  mention , "score": float(score[1])}
               json_answer_list.append(answer)
               #answer = "{\"publication_id\": " +  paper_id + ", \"mention\": \"" + mention + "\", \"score\": " + str(score[1]) + "}," 
   
    json.dump(json_answer_list, f)


if __name__ == '__main__':
  start_time = time.time() 
  config2 = config_parser.parser.parse_args()
  torch.manual_seed(config2.seed)
  #logging.basicConfig2(
    #filename=constant.EXP_ROOT +"/"+ config2.model_id + datetime.datetime.now().strftime("_%m-%d_%H") + config2.mode + '.txt',
    #level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
  #logging.info(config2)
  #logger = logging.getLogger()
  #logger.setLevel(logging.INFO)

  _test(config2)
  print("--- %s seconds ---" %(time.time() - start_time))