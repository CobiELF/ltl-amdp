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

# seq2seq functions
def init(input_lang, output_lang, encoder_checkpoint, decoder_checkpoint):
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

def getnexts(index, decoder, decoder_hidden, encoder_outputs):
    decoder_input = Variable(torch.LongTensor([[index]]))
    decoder_input = decoder_input.cuda() if use_cuda else decoder_input
    decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
    topv, topi = decoder_output.data.topk(decoder_output.size()[-1])
    nexts = []
    for i in np.arange(decoder_output.size()[-1]):
        next = topi[0][i].cpu().data.numpy().tolist()
        nextscore = topv[0][i].cpu().data.numpy()
        nexts.append((next, nextscore))
    return nexts, decoder_hidden

def translate(input_lang, output_lang, encoder, decoder, sentence, max_length, k):
    # encoding
    input_variable = variableFromSentence(input_lang, ' '.join(list(reversed(sentence.split()))))
    input_length = input_variable.size()[0]
    encoder_hidden = encoder.initHidden()
    encoder_outputs = Variable(torch.zeros(max_length, encoder.hidden_size))
    encoder_outputs = encoder_outputs.cuda() if use_cuda else encoder_outputs
    for ei in np.arange(input_length):
        encoder_output, encoder_hidden = encoder(input_variable[ei],
                                                 encoder_hidden)
        encoder_outputs[ei] = encoder_outputs[ei] + encoder_output[0][0]
    # beam search decoding of the one input sentence
    hidden = encoder_hidden
    index = SOS_token
    seqs = [([index], 0.0)]
    #print("translating:", sentence, flush=True)
    # for each decoded token in the sequence
    while index != EOS_token:
        # get the possible decodings of the next token, expand candidates
        candidates = list()
        nexts, hidden = getnexts(index, decoder, hidden, encoder_outputs)
        for seq, score in seqs:
            for next, nextscore in nexts:
                candidate = (seq + [next], score - nextscore)
                candidates.append(candidate)
        # order all candidates by score, select k best, follow best decoding path
        ordered = sorted(candidates, key=lambda t:t[1])
        seqs = ordered[:k]
        index = seqs[0][0][-1]
        #print(seqs2sentences(seqs), flush=True)
    return seqs

# helper functions
def seqs2sentences(seqs):
    sentences = list()
    for seq, score in seqs:
        sentence = ""
        for i in seq:
            if i!=SOS_token and i!=EOS_token:
                word = str(output_lang.index2word[i])
                sentence = sentence + word + " "
        sentences.append(sentence[0:-1])
    return sentences

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

# evaluation scripting
def eval(input_lang, output_lang, encoder, decoder, pairs, max_length, k):
    correct = 0
    total = 0
    print('sentence,', 'trueltl,', 'rank,', 'variants,', 'goodvariants', flush=True)
    for sentence, true_ltl in pairs:
        variants = seqs2sentences(translate(input_lang, output_lang, encoder, decoder, sentence, max_length, k))
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

def eval2(input_lang, output_lang, encoder, decoder, pairs, max_length, k):
    print('sentence,', 'variant,', 'correct,', 'trajectory,', 'translationtime,', 'solvetime', flush=True)
    for sentence, true_ltl in pairs:
        variants = seqs2sentences(translate(input_lang, output_lang, encoder, decoder, sentence, max_length, k))
        goodvariants = [variant for variant in variants if valid_ltl(variant)]
        for goodvariant in goodvariants:
            print("\""+str(sentence)+"\",", "\""+str(goodvariant)+"\",", str(true_ltl==goodvariant)+",", ",", ",", "", flush=True)

if __name__ == '__main__':
    # ALL
    input_lang, output_lang, pairs, max_length, max_tar_length = prepareData('ALL_SRC', 'ALL_TAR', False)
    pairs = []
    the_encoder, the_decoder = init(input_lang, output_lang, 'ENCODER_1', 'DECODER_1')
    # TRAIN
    #train_input_lang, train_output_lang, train_pairs, train_max_length, train_max_tar_length = prepareData('TRAIN_1_SRC', 'TRAIN_1_TAR', False)
    #eval(input_lang, output_lang, the_encoder, the_decoder, train_pairs, max_length, 10)
    # TEST
    test_input_lang, test_output_lang, test_pairs, test_max_length, test_max_tar_length = prepareData('TEST_1_SRC', 'TEST_1_TAR', False)
    eval2(input_lang, output_lang, the_encoder, the_decoder, test_pairs, max_length, 10)
