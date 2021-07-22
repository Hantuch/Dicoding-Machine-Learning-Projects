# -*- coding: utf-8 -*-
"""ML_Pengembangan_Image_Classifier_Submission_Hanif_Rachmadani

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qFn5XleDdJrFzfwqAd8bGS9APc8_AA2P
"""

# Dicoding Course "Belajar Pengembangan Machine Learning" 3rd Project: Advanced Image Classifier

# Animal Classifier

# Hanif Rachmadani on 16/07/2021.

# Dataset used : https://www.kaggle.com/madisona/translated-animals10

# TF & Data-prepping Libraries Import

import tensorflow as tf
from google.colab import files
import os, shutil

from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Dataset Download

files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json
!ls ~/.kaggle

!kaggle datasets download -d madisona/translated-animals10

!mkdir translated-animals10
!unzip translated-animals10.zip -d translated-animals10
!ls translated-animals10

# Unused Label Removal

# Note: only 3 label used from a total of 10 to simplify things

base_dir = 'translated-animals10/animals10/raw-img'

animals = os.listdir(base_dir)

class_label = ['dog','spider','chicken']

unused_label = [word for word in animals if word not in class_label]

for word in unused_label : shutil.rmtree(os.path.join(base_dir,word))

os.listdir(base_dir)

# Check Dataset Size Variations

from PIL import Image

total = 0

for animal in class_label:
  dir = os.path.join(base_dir, animal)
  y = len(os.listdir(dir))
  print(animal+':', y)
  total = total + y
  
  img_name = os.listdir(dir)
  for x in range(4):
    img_path = os.path.join(dir, img_name[x])
    img = Image.open(img_path)
    print('-',img.size)
  print('---------------')

print('\nTotal :', total)

# ImageDataGenerator (Data Augmentation) Instantiation

image_generator = ImageDataGenerator(
                    rescale=1./255,
                    width_shift_range=0.1,
                    height_shift_range=0.1,
                    rotation_range=20,
                    zoom_range=0.2,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest',
                    validation_split=0.2)

# Training Data Generation                

train_generator = image_generator.flow_from_directory(
                  base_dir,
                  target_size=(150,150),
                  batch_size=32,
                  class_mode='categorical',
                  subset='training')

# Validation Data Generation

validation_generator = image_generator.flow_from_directory(
                  base_dir,
                  target_size=(150,150),
                  batch_size=32,
                  class_mode='categorical',
                  subset='validation')

# Update Class Label Order

print(train_generator.class_indices)

class_label = ['chicken','dog','spider']

# Model Design

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),  # Input Layer/1st Convolution Layer : 150x150 px Image split into RGB
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),                             # 4 Convolution Layers
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(512, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),                                    # 3 Hidden Layer w/ 50%/20% Dropouts on Each Layer
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(3, activation='softmax')                                    # Output Layer
])

# Model Compilation

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.summary()

# Callback Declaration

acc_target = 0.92   # Set accuracy target

class modelCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > acc_target and logs.get('val_accuracy') > acc_target):  
      print("Accuracy Target of " + str(acc_target) + " on Both Training & Validation Data Reached, Stopping Training...")
      self.model.stop_training = True

# Model Training

history = model.fit(
      train_generator,
      batch_size=32,                            # 32 Data per Batch Loading
      steps_per_epoch=300,                      # 100 Batches Used per Epoch for Training
      epochs=100,                               # 100 Maximum Epoch (Arbitratry)
      validation_data=validation_generator,     
      validation_steps=75,                      # 75 Batches Used per Epoch for Validation
      callbacks=[modelCallback()],              # Callback
      verbose='auto')

# Pyplot Import

import matplotlib.pyplot as plt

# Loss & Accuracy Graph

plt.plot(history.history['loss'], color="orange")
plt.plot(history.history['val_loss'], color="red")
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train','Validation'], loc='upper right')
plt.show()

plt.plot(history.history['accuracy'], color="cyan")
plt.plot(history.history['val_accuracy'], color="blue")
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train','validation'], loc='lower right')
plt.show()

# Commented out IPython magic to ensure Python compatibility.
# Libraries Import

import numpy as np
from google.colab import files
from keras.preprocessing import image
import matplotlib.image as mpimg
# %matplotlib inline

# Upload File(s)

uploaded = files.upload()

# Prediction for Each Files

for fn in uploaded.keys():
 
  path = fn
  img = image.load_img(path, target_size=(150,150))
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)
  
  print(fn)
  print(class_label[np.argmax(classes)])

# Convert to TFLite

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
  f.write(tflite_model)