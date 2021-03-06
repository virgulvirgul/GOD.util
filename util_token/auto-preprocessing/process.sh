#!/bin/bash
#version2.0 revo,1/22/2018, AUTO-preprocessing en-zh,zh-en, and others
if [ "$1" == "-h"  ]; then
  echo 'Please modify your correct parameters.'
  echo 'Usage : ./AUTO-pre-processing.sh CORPUS'
    exit 0
fi
CORPUS=$1
TOKENIZER=~/GOD.util/super_tokenizer/super_tokenizer.py
UTIL_FOLDER=~/GOD.util/util_token
# GOD_FOLDER=~/GOD.util
SUPER="python "$TOKENIZER
# SUPER=/home/ubuntu/tools/super_tokenizer/super_tokenizer
echo "language order : en->zh && zh->en"
$SUPER en < $CORPUS.en > $CORPUS.tok.en
$SUPER zh < $CORPUS.zh > $CORPUS.tok.zh
# en->zh
$UTIL_FOLDER/escape-special-chars.perl < $CORPUS.tok.zh > $CORPUS.en-zh.esc.zh
tr [:upper:] [:lower:] < $CORPUS.tok.en > $CORPUS.en-zh.tok.en
mv $CORPUS.en-zh.esc.zh $CORPUS.en-zh.tok.zh
# zh->en
$UTIL_FOLDER/replace-unicode-punctuation.perl < $CORPUS.tok.zh > $CORPUS.replace.zh
$UTIL_FOLDER/escape-special-chars.perl < $CORPUS.replace.zh > $CORPUS.zh-en.esc.zh
cp $CORPUS.tok.en $CORPUS.zh-en.tok.en
mv $CORPUS.zh-en.esc.zh $CORPUS.zh-en.tok.zh

rm $CORPUS.tok.en
rm $CORPUS.tok.zh
rm $CORPUS.replace.zh

