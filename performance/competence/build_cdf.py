#!/usr/bin/env python
# coding=utf-8
# Copyright 2018 The THUMT Authors

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import collections
import math
import numpy as np

def count_words(filename):
    counter = collections.Counter()

    with open(filename, "r") as fd:
        for line in fd:
            words = line.strip().split()
            counter.update(words)

    count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    words, counts = list(zip(*count_pairs))

    return words, counts


def control_symbols(string):
    if not string:
        return []
    else:
        return string.strip().split(",")
        
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    # Reverse way to do softmax
    MAX_VALUE = max(x)
    x = MAX_VALUE / np.array(x)
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0) # only difference
        
def word_pro_cal(pro, T_freq):
  if args.emb_vector:
    # MAX_EMB_MOD = 11.0
    # return 1 - (pro / MAX_EMB_MOD)
    return pro
  return pro / T_freq

def save_vocab(name, vocab):
    print ("Calculating Pro for each word!")
    if name.split(".")[-1] != "txt":
        name = name + ".txt"

    # pairs = sorted(vocab.items(), key=lambda x: (x[1], x[0]))
    pairs = sorted(vocab.items(), key=lambda x: x[1], reverse=True)
    words, ids = list(zip(*pairs))

    # if args.emb_vector:
    #   ids = softmax(ids)
    #   print (ids)
    # total freq
    T_freq = sum(ids)

    with open(name, "w") as f:
        for i, word in enumerate(words):
            f.write(word + " " + "%.16f" % word_pro_cal(ids[i], T_freq) + "\n")
        
    # map of freq
    freq_dict = {}
    for word, id in zip(words, ids):
        freq_dict[word] = id
    return freq_dict, T_freq

def cal_cdf_model(corpus, freq_dict, T_freq):
    print ("=" * 100)
    print ("Calculating CDF MODEL")
    print ("T_freq:%d" % T_freq)
    data = []
    debug = 0
    with open(corpus, "r") as f:
        for line in f.readlines():
            line = line.split()
            SUM = 0
            for w in line:
                p = word_pro_cal(freq_dict[w], T_freq)
                if p != 0:
                    # SUM += math.log(p)
                    SUM += p
            # SUM = -SUM
            data.append(SUM)
            # if SUM < 5.718:
            #     debug += 1
            #  print (SUM)
    # data contains all sum log
    # bins='auto', paper is 1000
    v, base = np.histogram(data, bins=np.arange(400))
    print ("data:", data[:50])
    print ("value", v[:50])
    base = base.astype(np.float32)
    print ("base:", base[:50])
    print ("highest value:", base[-1])
    print ("len of base:", len(base))
    # print ("debug:", debug)
    cdf = np.cumsum(v)
    cdf = cdf / len(data)
    cdf = cdf.astype(np.float32)
    print ("cdf:", cdf, cdf.dtype)
    print ("outputing cdf and bases.")
    # res = {"cdf": cdf, "base": base}
    np.savez(args.output + "-cdf_base.npz", cdf=cdf, base=base)

def MOD(data):
  sum = 0.0
  for f in data:
    sum += f * f
  sum = sum ** 0.5
  return sum
    
def parse_word_emb(file):
    import codecs
    emb = codecs.open(file, 'r', encoding="utf-8").readlines()
    vocab_size, dim = emb[0].split()
    emb = emb[1:]
    res = {}
    for line in emb:
      line = line.split()
      word = line[0]
      data = [float(i) for i in line[1:]]
      mod = MOD(data)
      res[word] = mod
    return res

def parse_args():
    parser = argparse.ArgumentParser(description="Create vocabulary")

    parser.add_argument("corpus", help="input corpus")
    parser.add_argument("output", default="en",
                        help="Output prefix name")
    parser.add_argument("--limit", default=0, type=int, help="Vocabulary size")
    parser.add_argument("--emb_vector", default="", type=str, help="Using Embedding vector to calculate C of each sent. Embedding file")
    parser.add_argument("--control", type=str, default="",
                        help="Add control symbols to vocabulary. "
                             "Control symbols are separated by comma.")

    return parser.parse_args()

args = parse_args()

def main():
    vocab = {}
    limit = args.limit
    count = 0

    words, counts = count_words(args.corpus)
    ctrl_symbols = control_symbols(args.control)

    for sym in ctrl_symbols:
        vocab[sym] = len(vocab)

    # load emb
    if args.emb_vector:
      emb = parse_word_emb(args.emb_vector)

    for word, freq in zip(words, counts):
        if limit and len(vocab) >= limit:
            break

        if word in vocab:
            print("Warning: found duplicate token %s, ignored" % word)
            continue

        # vocab[word] = len(vocab)
        # print(word, freq)
        if args.emb_vector:
          # if not word in emb:
          #   print ("Out of vocab", word)
          score = emb.get(word, 10.0)
          # print(word, score)
          vocab[word] = score
        else:
          vocab[word] = freq
          count += freq

    freq_dict, T_freq = save_vocab(args.output, vocab)
    cal_cdf_model(args.corpus, freq_dict, T_freq)

    print("Total words: %d" % sum(counts))
    print("Unique words: %d" % len(words))
    print("Vocabulary coverage: %4.2f%%" % (100.0 * count / sum(counts)))


if __name__ == "__main__":
    main()