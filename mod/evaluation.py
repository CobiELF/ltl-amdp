# imports
from __future__ import print_function, division
import sys
import copy
import random
import numpy as np
import itertools
sys.path.insert(0, '/home/ndanas/repos/ltl-amdp/lggltl/models/torch/')
from lang import *
from networks import *
from train_eval import *
from train_langmod import *
from utils import *
from lark import Lark

# constants
use_cuda = torch.cuda.is_available()
SEED = 1;
random.seed(SEED)
torch.manual_seed(SEED) if not use_cuda else torch.cuda.manual_seed(SEED)
embed_size = 50
hidden_size = 256
all_src, all_tar, train_src, train_tar, test_src, test_tar = 'ALL_SRC', 'ALL_TAR', 'TRAIN_SRC', 'TRAIN_TAR', 'TEST_SRC', 'TEST_TAR'
encoder_checkpoint = 'ENCODER'
decoder_checkpoint = 'DECODER'

# functions
def init(input_lang, output_lang):
    the_encoder = EncoderRNN(input_lang.n_words, embed_size, hidden_size)
    the_decoder = AttnDecoderRNN(embed_size, hidden_size, output_lang.n_words)
    if use_cuda:
        the_encoder = encoder1.cuda()
        the_decoder = attn_decoder1.cuda()
    the_encoder.load_state_dict(torch.load(encoder_checkpoint))
    the_decoder.load_state_dict(torch.load(decoder_checkpoint))
    the_encoder.eval()
    the_decoder.eval()
    return the_encoder, the_decoder

def getnis(index, decoder, decoder_hidden, encoder_outputs, k=1):
    decoder_input = Variable(torch.LongTensor([[index]]))
    decoder_input = decoder_input.cuda() if use_cuda else decoder_input
    decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
    topv, topi = decoder_output.data.topk(k)
    nis = []
    for i in range(k):
        nis.append(topi[0][i].cpu().data.numpy().tolist())
    return nis, decoder_hidden

def translate(input_lang, output_lang, encoder, decoder, sentence, max_length, k):
    input_variable = variableFromSentence(input_lang, ' '.join(list(reversed(sentence.split()))))
    input_length = input_variable.size()[0]
    encoder_hidden = encoder.initHidden()
    encoder_outputs = Variable(torch.zeros(max_length, encoder.hidden_size))
    encoder_outputs = encoder_outputs.cuda() if use_cuda else encoder_outputs
    for ei in range(input_length):
        encoder_output, encoder_hidden = encoder(input_variable[ei],
                                                 encoder_hidden)
        encoder_outputs[ei] = encoder_outputs[ei] + encoder_output[0][0]
    # expand the first seq, keeping track of alternative branches at each step
    seqs = ["SOS"]
    hidden = encoder_hidden
    index = SOS_token
    while index != EOS_token:
        nis, hidden = getnis(index, decoder, hidden, encoder_outputs, k)
        nextseqs = []
        # alternative steps are products of the branches
        nexts = [output_lang.index2word[i] for i in nis]
        # avoid products that affect grammatical structure
        if "(" not in nexts[0] and ")" not in nexts[0]:
            for next in nexts:
                for seq in seqs:
                    nextseq = seq+" "+next
                    nextseqs.append(nextseq)
        else:
            for seq in seqs:
                nextseq = seq+" "+nexts[0]
                nextseqs.append(nextseq)
        seqs = nextseqs
        # just follow the first seq, since it's the only one likely to be grammatically correct
        index = nis[0]
    return [seq[4:-4] for seq in seqs]

def valid_ltl(grounding):
    grammar = """
        ltl: "X " ltl
           | "F " ltl
           | "G " ltl
           | "~ " ltl
           | ltl " & " ltl
           | ltl " U " ltl
           | "(" ltl ")"
           | prim
           | "~" prim

        prim: "red_room" | "orange_room" | "yellow_room" | "green_room" | "blue_room" | "purple_room"
            | "landmark_1" | "landmark_2" | "landmark_3" | "landmark_4" | "landmark_5"
            | "first_floor" | "second_floor" | "third_floor" | "fourth_floor" | "fifth_floor"

        %import common.WS
        %ignore WS
    """
    parser = Lark(grammar, start='ltl', ambiguity='explicit')
    try:
        tree = parser.parse(grounding)
        return True
    except:
        return False

def eval(input_lang, output_lang, encoder, decoder, pairs, max_length, k):
    correct = 0
    total = 0
    print('sentence,', 'trueltl,', 'rank,', 'variants,', 'goodvariants', flush=True)
    for sentence, true_ltl in pairs:
        variants = translate(input_lang, output_lang, encoder, decoder, sentence, max_length, k)
        goodvariants = [variant for variant in variants if valid_ltl(variant)]
        if true_ltl in goodvariants:
            correct = correct+1
        total = total+1
        ranks = [rank for rank,goodvariant in enumerate(goodvariants) if goodvariant == true_ltl]
        rank = -1
        if len(ranks)>0:
            rank = ranks[0]
        print("\""+str(sentence)+"\",", "\""+str(true_ltl)+"\",", str(rank)+",", str(len(variants))+",", str(len(goodvariants)), flush=True)
    print("Final Accuracy:", correct/total)

# main
if __name__ == '__main__':
    # ALL
    input_lang, output_lang, pairs, max_length, max_tar_length = prepareData(all_src, all_tar, False)
    pairs = []
    the_encoder, the_decoder = init(input_lang, output_lang)
    # TRAIN
    train_input_lang, train_output_lang, train_pairs, train_max_length, train_max_tar_length = prepareData(train_src, train_tar, False)
    eval(input_lang, output_lang, the_encoder, the_decoder, train_pairs, max_length, 2)
    # TEST
    #test_input_lang, test_output_lang, test_pairs, test_max_length, test_max_tar_length = prepareData(test_src, test_tar, False)
    #eval(input_lang, output_lang, the_encoder, the_decoder, test_pairs, max_length, 2)

