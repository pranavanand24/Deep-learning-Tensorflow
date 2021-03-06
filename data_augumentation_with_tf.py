# -*- coding: utf-8 -*-
"""Data Augumentation with TF.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iGilR7ZRDvuOrYRgszGapFvLCcQUtn0J
"""

pip install -q git+https://github.com/tensorflow/docs

import urllib

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras import layers
AUTOTUNE = tf.data.experimental.AUTOTUNE

import tensorflow_docs as tfdocs
import tensorflow_docs.plots

import tensorflow_datasets as tfds

import PIL.Image

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = (12, 5)

import numpy as np

image_path = tf.keras.utils.get_file("cat.jpg", "https://storage.googleapis.com/download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg")
PIL.Image.open(image_path)

image_string = tf.io.read_file(image_path)
image = tf.image.decode_jpeg(image_string, channels=3)

def visualize(original, augmented):
  fig = plt.figure()
  plt.subplot(1,2,1)
  plt.title('Original image')
  plt.imshow(original)

  plt.subplot(1,2,2)
  plt.title('Augmented image')
  plt.imshow(augmented)

"""**Flipping the image**"""

flipped = tf.image.flip_left_right(image)
visualize(image, flipped)

"""**Grayscale the image**"""

grayscaled = tf.image.rgb_to_grayscale(image)
visualize(image, tf.squeeze(grayscaled))
plt.colorbar()

"""**Saturate the image**"""

saturated = tf.image.adjust_saturation(image, 3)
visualize(image, saturated)

"""**Change image brightness**"""

bright = tf.image.adjust_brightness(image, 0.4)
visualize(image, bright)

"""**Rotate the image**"""

rotated = tf.image.rot90(image)
visualize(image, rotated)

"""**Center crop the image**"""

cropped = tf.image.central_crop(image, central_fraction=0.5)
visualize(image,cropped)

"""**Augument a dataset and train a model with it**"""

dataset, info =  tfds.load('mnist', as_supervised=True, with_info=True)
train_dataset, test_dataset = dataset['train'], dataset['test']

num_train_examples= info.splits['train'].num_examples

def convert(image, label):
  image = tf.image.convert_image_dtype(image, tf.float32) 
  return image, label

def augment(image,label):
  image,label = convert(image, label)
  image = tf.image.convert_image_dtype(image, tf.float32) 
  image = tf.image.resize_with_crop_or_pad(image, 34, 34) 
  image = tf.image.random_crop(image, size=[28, 28, 1])
  image = tf.image.random_brightness(image, max_delta=0.5) 

  return image,label

BATCH_SIZE = 64

NUM_EXAMPLES = 2048

augmented_train_batches = (
    train_dataset
    # Only train on a subset, so you can quickly see the effect.
    .take(NUM_EXAMPLES)
    .cache()
    .shuffle(num_train_examples//4)
    # The augmentation is added here.
    .map(augment, num_parallel_calls=AUTOTUNE)
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)

non_augmented_train_batches = (
    train_dataset
    # Only train on a subset, so you can quickly see the effect.
    .take(NUM_EXAMPLES)
    .cache()
    .shuffle(num_train_examples//4)
    # No augmentation.
    .map(convert, num_parallel_calls=AUTOTUNE)
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)

validation_batches = (
    test_dataset
    .map(convert, num_parallel_calls=AUTOTUNE)
    .batch(2*BATCH_SIZE)
)

def make_model():
  model = tf.keras.Sequential([
      layers.Flatten(input_shape=(28, 28, 1)),
      layers.Dense(4096, activation='relu'),
      layers.Dense(4096, activation='relu'),
      layers.Dense(10)
  ])
  model.compile(optimizer = 'adam',
                loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])
  return model

"""**Train the model without augumentation**"""

model_without_aug = make_model()

no_aug_history = model_without_aug.fit(non_augmented_train_batches, epochs=50, validation_data=validation_batches)

"""**Train it again with augmentation**"""

model_with_aug = make_model()

aug_history = model_with_aug.fit(augmented_train_batches, epochs=50, validation_data=validation_batches)