#! /usr/bin/env python

from flask import Flask
from flask import request

from pycorenlp import StanfordCoreNLP

import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN
from tensorflow.contrib import learn
import csv
import itertools


app = Flask(__name__)

print("make sure to first train model in train_cnn.py")
# Parameters
# ==================================================

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_dir", "./runs/1488949423/checkpoints/", "Checkpoint directory from training run")
tf.flags.DEFINE_boolean("eval_train", False, "Evaluate on all training data")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

acts_name = ["Information Sharing","Shared Understanding","Other"]

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")

x_raw = ["this is just an example text", "all is not on."]
y_test = [1, 0]

# Map data into vocabulary
vocab_path = os.path.join(FLAGS.checkpoint_dir, "..", "vocab")
vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)

print("\nEvaluating...\n")

# Evaluation
# ==================================================
checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name("output/predictions").outputs[0]

print("Done loading CNN model into memory!")

print("Now setting up tree parsers with Stanford CoreNLP!")

nlp = StanfordCoreNLP('http://localhost:9000')
def split_sentences(text):
	out = []
	for sentence_dirty in text:
		word_units = sentence_dirty.split(" ")
		sentence = ""
		for word_dirty in word_units:
			if len(word_dirty) < 1:
				continue
			if word_dirty[-1] == ")":
				word_dirty = word_dirty.replace(")","")
				sentence += " " + word_dirty
		if len(sentence) > 1:
			out += [sentence]
	return out

def parse_sentences(text):
	output = nlp.annotate(text, properties={
	    'annotators': 'tokenize,ssplit,pos,depparse,parse',
	    'outputFormat': 'json'
	})
	if len(output['sentences']) < 1:
		return ['']
	text = output['sentences'][0]['parse']

	text = str(text)
	text = ' '.join(text.split())
	sentences_dirty = text.split("(SBAR")
	return sentences_dirty

@app.route('/')
def index():

    #get utterance from request data
    utterance = request.args.get('utterance')
    text = (utterance)

    #separating transcript by sentence endings
    sentences_dirty = parse_sentences(str(text))
    utterances = split_sentences(sentences_dirty)

    unit_out = ""
    for utt in utterances:
        #loop through sentences
        x_test = np.array(list(vocab_processor.transform([utterance])))
        batches = data_helpers.batch_iter(list(x_test), FLAGS.batch_size, 1, shuffle=False)
        for x_test_batch in batches:
            batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
        unit_out += str(utt) + ";" + str(acts_name[batch_predictions[0]]) + "-"
    return unit_out

if __name__ == '__main__':
    print("starting server")
    app.run(debug=True)












