# Title:    Fluffy - A REST Image Processer
# Author:   Riccardo Carissimi
# Desc:     Given a photo, returns the objects it displays (thanks to Tensorflow)
# Some pieces of code are taken from https://tensorflow.org/tutorials/image_recognition/

# TO INSTALL: 
# Python VERSION 3.6
# Tensorflow > https://www.tensorflow.org/install/pip
# PIP - mysql-connector-python flask flask-cors
# mysql server

# ++ TENSORFLOW IMPORTS and GLOBALS ++

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os.path
import re
import sys
import tarfile

import numpy as np
from six.moves import urllib
import tensorflow as tf

FLAGS = None

# pylint: disable=line-too-long
DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
#DATA_URL = 'http://download.tensorflow.org/models/inception_v4_2016_09_09.tar.gz'
# pylint: enable=line-too-long

# ++ REST API IMPORTS and GLOBALS ++ 

# Imports
from flask import (
    Flask,
    render_template,
    jsonify,
    request
)

import shutil

import subprocess

import urllib.request
import requests

#Cross Origin Requests
from flask_cors import CORS

#ImageHash
import hashlib

#Script's directory name
import os

#TempFile
import tempfile

#Globals
IMG_SERVICE_LINK = "https://i.imgur.com/"
TMP_IMG_PATH = "/tmp/tf_img"
SERVER_PORT = "5000"

#Tensorflow model's dir (script's path + models folder)
MODEL_DIR = os.path.dirname(os.path.realpath(__file__)) + '/models'

# ++ NODE ID to STRING Converter ++

class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = os.path.join(
          MODEL_DIR, 'imagenet_2012_challenge_label_map_proto.pbtxt')
    if not uid_lookup_path:
      uid_lookup_path = os.path.join(
          MODEL_DIR, 'imagenet_synset_to_human_label_map.txt')
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.

    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.

    Returns:
      dict from integer node ID to human-readable string.
    """

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.io.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.io.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]

# ++ TENSORFLOW FUNCTIONS ++

def create_graph():
  """Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.
  with tf.io.gfile.GFile(os.path.join(
      MODEL_DIR, 'classify_image_graph_def.pb'), 'rb') as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

def maybe_download_and_extract():
  """Download and extract model tar file."""
  dest_directory = MODEL_DIR
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):
    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' % (
          filename, float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()
    filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
    print()
    statinfo = os.stat(filepath)
    print('Successfully downloaded', filename, statinfo.st_size, 'bytes.')
  tarfile.open(filepath, 'r:gz').extractall(dest_directory)

def run_inference_on_image(image):
  """Runs inference on an image.

  Args:
    image: Image file name.

  Returns:
    First result
  """
  NUM_RESULTS = 1

  image_data = tf.io.gfile.GFile(image, 'rb').read()

  # Creates graph from saved GraphDef.
  create_graph()

  with tf.compat.v1.Session() as sess:
    # Some useful tensors:
    # 'softmax:0': A tensor containing the normalized prediction across
    #   1000 labels.
    # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
    #   float description of the image.
    # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
    #   encoding of the image.
    # Runs the softmax tensor by feeding the image_data as input to the graph.
    softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
    predictions = sess.run(softmax_tensor,
                           {'DecodeJpeg/contents:0': image_data})
    predictions = np.squeeze(predictions)

    # Creates node ID --> English string lookup.
    node_lookup = NodeLookup()

    #top_k = predictions.argsort()[-FLAGS.num_top_predictions:][::-1]
    top_k = predictions.argsort()[-NUM_RESULTS:][::-1]
    for node_id in top_k:
      human_string = node_lookup.id_to_string(node_id)
      score = predictions[node_id]
      #print('{"object":"%s","score": %.5f}' % (human_string, score))
      cmd_output = '{"object":"%s","score": %.5f}' % (human_string, score)
      #print(cmd_output)
  
  return cmd_output

# ++ REST API ++

# Create the application instance
app = Flask(__name__, template_folder="templates")

#Allow Cross Origins
CORS(app)

# Create a URL route in our application for "/api/img_id?deletetoken=***"
@app.route('/api/<id>', methods=['GET', 'POST'])
def api(id):

    print("[INFO] Received request")
    
    deletetoken = request.args["deletetoken"]

    #TMP File Creation
    tmp = tempfile.NamedTemporaryFile(mode="w+b")
    TMP_IMG_PATH = tmp.name

    print("[INFO] Image file path: " + TMP_IMG_PATH)

    # Image Download
    imgur_link = IMG_SERVICE_LINK + id
    image = requests.get(imgur_link)
    tmp.write(image.content)

    print("[INFO] Image Downloaded")

    #Image Hash
    hasher = hashlib.md5()
    tmp.seek(0)
    hasher.update(tmp.read())
    print("[INFO] Image Hash: " + hasher.hexdigest())

    print("[INFO] Processing image...")

    # Command Execution
    # cmd_output = subprocess.check_output(COMMAND, shell=True)
    cmd_output = run_inference_on_image(TMP_IMG_PATH)
    
    print("[INFO] Elaborated result: " + cmd_output)

    # Get Only the First Result "jsonified"
    #cmd_output = cmd_output.decode().split('\n', 1)[0]

    #Closes the file
    tmp.close()
    # Return the result
    return jsonify(eval(cmd_output))

if __name__ == '__main__':

  # classify_image_graph_def.pb:
  #   Binary representation of the GraphDef protocol buffer.
  # imagenet_synset_to_human_label_map.txt:
  #   Map from synset ID to a human readable string.
  # imagenet_2012_challenge_label_map_proto.pbtxt:
  #   Text representation of a protocol buffer mapping a label to synset ID.
  maybe_download_and_extract()
  app.run(port=SERVER_PORT, host="0.0.0.0")
