# -*- coding: utf-8 -*-
"""STELLAR.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ch0MUE1tAj6aUBWFWzjqvr3XJL1eJ1Qv
"""

# Author - Danish Gufran
# Danish.Gufran@colostate.edu

# Citation : https://ieeexplore.ieee.org/document/10323477

'''
STELLAR: Siamese Multi-Headed Attention Neural Networks for Overcoming
Temporal Variations and Device Heterogeneity
With Indoor Localization
'''

# !rm -rf maril
try:
  !git clone https://github.com/danishgufran/RSS_Database.git
  !git clone https://github.com/danishgufran/EPIC_Lab_Data.git
  !git clone https://github.com/EPIC-CSU/heterogeneous-rssi-indoor-nav.git
  !pip install tensorflow-addons
  !pip install keras-multi-head
  !pip install catboost

except:
  from git import Repo  # pip install gitpython
  Repo.clone_from("https://github.com/danishgufran/RSS_Database.git")
  Repo.clone_from("https://github.com/danishgufran/EPIC_Lab_Data.git")
  Repo.clone_from("https://github.com/EPIC-CSU/heterogeneous-rssi-indoor-nav.git")

import numpy as np

import copy
from copy import deepcopy
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import *
from tensorflow.keras.layers import Dense, Dropout, Flatten, Reshape
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Conv1D, MaxPooling1D , LSTM, Attention
from tensorflow.keras.losses import *
from tensorflow.keras.optimizers import*
import random as random
import time
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd

import RSS_Database.Stone_Seth.Seth
from RSS_Database.Stone_Seth.Seth import fetch_seth, Devices, Floorplan, get_mac_ids

from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from EPIC_Lab_Data.data import Devices, Floorplan, build_dataset
from EPIC_Lab_Data.helpers import compute_distances
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

from tensorflow.keras import layers
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Model

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import lightgbm as lgb

import logging
import json
import numpy as np
import os
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow import keras
from tensorflow.keras.layers import LayerNormalization
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, LayerNormalization, MultiHeadAttention, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.losses import Loss
from tensorflow.keras.optimizers import Adam
from sklearn import svm
import xgboost as xgb

from EPIC_Lab_Data.helpers import split_frame, compute_distances
from EPIC_Lab_Data.data import build_dataset
from EPIC_Lab_Data.Maril.MultiHeadAttentionAddon import MultiHeadAttentionAddon

def train_data(itr,dev, floorplan):
    # dfs is a list of dataframes
# meta is a dataframe with meta data

#getting train data

    train_fp, train_meta = fetch_seth(
    dev,
    str(floorplan),
    ci = int(itr),
    base_path="RSS_Database/Stone_Seth/temp/clean/"  # <-- this would be 'seth/temp/clean' from outside this dir
)
    # train_fp, _, macs, lbl2cord = build_dataset(
    #     dev,
    #     str(floorplan),
    # )
    train_fp = train_fp.sample(frac=1).reset_index(drop=True)
    train_aps = get_mac_ids(train_fp.columns)
    train_x = train_fp[train_aps].values
    # train_x = (train_x + 100)/100
    train_y = (train_fp["label"]).values
    return train_x, train_y, train_aps

def test_data(itr, train_aps, dev, floorplan):
    #getting test data
    test_fp, test_meta = fetch_seth(
    dev ,
    str(floorplan),
    ci = itr,
    base_path="RSS_Database/Stone_Seth/temp/clean/"  # <-- this would be 'seth/temp/clean' from outside this dir
)
    # train_df, test_fp, macs_test, lbl2cords = build_dataset(
    #       dev,
    #       str(floorplan)
    #   )
    test_y = test_fp["label"].values
    # train_aps = train_aps.drop(['x', 'y','label'], axis=1)
    # print(f'label -- {test_y}')
    test_aps = get_mac_ids(test_fp.columns)
    missing_aps = list(set(train_aps.columns)-set(test_aps))
    test_fp[missing_aps] = 0

    test_fp = test_fp.drop(['x', 'y','label'], axis=1)
    test_x = test_fp[:]

    # test_x = (test_x + 100)/100


    return test_x, test_y

def temp_train_data(dev, floorplan, ci_val):
    # dfs is a list of dataframes
# meta is a dataframe with meta data

#getting train data

    train_fp, train_meta = fetch_seth(
    dev,
    str(floorplan),
    ci = ci_val,
    base_path="RSS_Database/Stone_Seth/temp/clean/"  # <-- this would be 'seth/temp/clean' from outside this dir
)
    # train_fp, _, macs, lbl2cord = build_dataset(
    #     dev,
    #     str(floorplan),
    # )
    train_fp = train_fp.sample(frac=1).reset_index(drop=True)
    train_aps = get_mac_ids(train_fp.columns)
    train_x = train_fp[train_aps].values
    train_x = (train_x + 100)/100
    train_y = (train_fp["label"]).values
    return train_x, train_y, train_aps
def temp_test_data(train_aps, dev, floorplan, ci_val):
    #getting test data
    test_fp, test_meta = fetch_seth(
    str(dev) ,
    str(floorplan),
    ci = ci_val,
    base_path="RSS_Database/Stone_Seth/temp/clean/"  # <-- this would be 'seth/temp/clean' from outside this dir
)
    # train_df, test_fp, macs_test, lbl2cords = build_dataset(
    #       dev,
    #       str(floorplan)
    #   )
    test_aps = get_mac_ids(test_fp.columns)
    missing_aps = list(set(train_aps)-set(test_aps))
    test_fp[missing_aps] = 0
    test_x = test_fp[train_aps].values
    test_x = (test_x + 100)/100
    test_y = (test_fp["label"]).values
    return test_x, test_y

class Anvil:
    """
    Manage and build model
    NOTE: Lacks configurability; Needs fixing.
    """

    def __init__(
        self,
        train_device,
        floorplan,
        num_heads=7,
        head_size=50,
        data_path="EPIC_Lab_Data/Data",
        model_path="EPIC_Lab_Data/Maril/saved_models",
        model_name=None,
    ):
        self.device = train_device
        self.floorplan = floorplan
        self.data_path = data_path
        self.model_path = model_path
        self.num_heads = num_heads
        self.head_size = head_size
        self.final = []


        self.model = None

        _, _, self.macs, _ = build_dataset(
            self.device,
            self.floorplan,
            base_path=self.data_path,
        )

        # build meta
        self.meta = {
            "NUM_HEADS": num_heads,
            "HEAD_SIZE": head_size,
            "MACS": list(self.macs),
            "TRAIN_DEVICE": self.device,
            "TRAIN_FLOORPLAN": self.floorplan,
        }

        if model_name is None:
            self.model_name = f"DA_{train_device}_{floorplan}"
        else:
            self.model_name = model_name

    def build(self):

        train_df, _, macs, lbl2cords = build_dataset(
            self.device,
            self.floorplan,
            base_path=self.data_path,
        )

        td = self.device
        train_df_rst, _, train_macs_rst, lbl2cord_rst = build_dataset(
          td,
          self.floorplan,
      )
        missing_waps_rst = list(set(macs) - set(train_macs_rst))
        _df = train_df_rst.copy()  # supresses fragmented df warning
        _df[missing_waps_rst] = 0.0
        keys = _df[train_macs_rst].values.astype(float)
        values = keras.utils.to_categorical(_df["label"].values.astype(int))

        if self.floorplan == 'engr0':
          shp = len(set(train_macs_rst)) + 1

        if self.floorplan == 'engr1':
          shp = len(set(train_macs_rst))

        input_shape = shp
        output_shape = len(lbl2cords.keys())
        # keys = train_df[macs].values.astype(float)
        # values = keras.utils.to_categorical(train_df["label"].values.astype(int))

        # input
        input_layer = tf.keras.Input(shape=input_shape, name="query")
        x = input_layer
        print(input_shape)

        # augmentation # FASt Layer?
        if "NODA" in self.model_name:
            pass
        else:
            x = keras.layers.Normalization()(x)
            x = keras.layers.Dropout(0.1)(x)


            # x = MaskedDropout(0.10)(x)
            # x = MaskedRandomBrightness(0.10, is_img=False)(x)
            # x = MaskedRandomContrast(0.10, is_img=False)(x)

        # noise
        x = keras.layers.GaussianNoise(0.12)(x)

        # MultiHeadLayer
        x = MultiHeadAttentionAddon(
            head_size=self.head_size,
            num_heads=self.num_heads,
            # output_size=None,
            name="MHA",
            dropout=0.10,
        )([x, keys, values])

        # DNN layers
        x = keras.layers.Dense(50, activation="relu")(x)
        x = keras.layers.Dropout(0.10)(x)
        x = keras.layers.Dense(100, activation="relu")(x)
        x = keras.layers.Dropout(0.10)(x)

        # output layer
        output_layer = keras.layers.Dense(output_shape, activation="softmax")(x)

        # Connect the input and output model
        self.model = tf.keras.Model(
            inputs=input_layer, outputs=output_layer, name=self.model_name
        )
        return self.model

    def create_siamese_network(self, input_shape, num_heads, key_dim, dff, embedding_dim):
        output_classes = 61

        input_anchor = Input(shape=input_shape, name='anchor_input')
        input_positive = Input(shape=input_shape, name='positive_input')
        input_negative = Input(shape=input_shape, name='negative_input')

        shared_embedding = Dense(dff)

        multihead_attention = MultiHeadAttention(num_heads=num_heads, key_dim=key_dim)
        attention_layer_norm = LayerNormalization()
        flatten = Flatten()

        embedded_anchor = shared_embedding(input_anchor)
        embedded_positive = shared_embedding(input_positive)
        embedded_negative = shared_embedding(input_negative)

        # One-hot encode train_y
        train_y_input_tensor = Input(shape=(output_classes,), name='train_y_input')

        attention_anchor = self.model(input_anchor)
        attention_positive = self.model(input_positive)
        attention_negative = self.model(input_negative)

        attention_anchor = attention_layer_norm(attention_anchor)
        attention_positive = attention_layer_norm(attention_positive)
        attention_negative = attention_layer_norm(attention_negative)

        embedded_anchor = Dense(embedding_dim, activation='relu')(flatten(attention_anchor))
        embedded_positive = Dense(embedding_dim, activation='relu')(flatten(attention_positive))
        embedded_negative = Dense(embedding_dim, activation='relu')(flatten(attention_negative))

        # Use shape of train_y in Softmax layer
        softmax_output = Dense(output_classes, activation='softmax', name='softmax_output')(embedded_anchor)

        siamese_model = Model(
            inputs=[input_anchor, input_positive, input_negative, train_y_input_tensor],
            outputs=[embedded_anchor, embedded_positive, embedded_negative, softmax_output]
        )
        return siamese_model

# This is just to test
def shuffle_arrays(data_array):
    np.random.shuffle(data_array)
    return data_array

# This is just to test
def reverse_arrays(data_array):
    reversed_data_array = np.flip(data_array, axis=0)
    return reversed_data_array


def replace_with_zeros(array, replace_percent):
    num_samples = array.shape[0]
    num_features = array.shape[1]
    num_replacements = int(num_samples * num_features * replace_percent)

    # Flatten the array
    flattened_array = array.flatten()

    # Get random indices for replacements
    replace_indices = np.random.choice(num_samples * num_features, num_replacements, replace=True)

    # Replace selected indices with zeros
    flattened_array[replace_indices] = 0

    # Reshape back to original shape
    modified_array = flattened_array.reshape((num_samples, num_features))

    return modified_array

class TripletLoss(Loss):
    def call(self, y_true, y_pred):
        anchor, positive, negative = y_pred[:, 0], y_pred[:, 1], y_pred[:, 2]
        distance_positive = tf.reduce_sum(tf.square(anchor - positive), axis=-1)
        distance_negative = tf.reduce_sum(tf.square(anchor - negative), axis=-1)
        return tf.maximum(distance_positive - distance_negative + 0.2, 0.0)
        # return tf.maximum(distance_positive - distance_negative , 0.0)

# Functions Below :

train_dev = ['OP3']

dev = ['BLU','HTC','LG','MOTO','OP3','S7']

floorplan = ['engr0', 'engr1']

# Drop D% of APs Randomly
D_percent_drop = 0.60

# CI Start to test
ci_initial = 0

# CI Max to test
ci_max = 10

# Hyper-Parameter(s)
num_heads = 5
key_dim = 64
dff = 128
embedding_dim = 64
batchsize = 32
epoch = 100

for train in train_dev:
    for flp in floorplan:
        print(f'\n Train dev -> {train}   flp -> {flp} \n')
        # Initial CI only !!!
        ci_val = 0
        train_x, train_y, train_aps = temp_train_data(train, flp, ci_val)

        # Example usage
        input_shape = train_x.shape[1:]  # Exclude batch size
        output_classes = train_y.shape[-1]  # Number of output classes

        anvil_instance = Anvil(train, flp)
        model = anvil_instance.build()  # Build the Anvil model
        siamese_model = anvil_instance.create_siamese_network(
            input_shape=input_shape,
            num_heads=num_heads,
            key_dim=key_dim,
            dff=dff,
            embedding_dim=embedding_dim
        )
        siamese_model.summary()

        # Compile the model with triplet loss
        siamese_model.compile(optimizer=Adam(learning_rate=0.00001), loss=TripletLoss())

        train_x_modified = replace_with_zeros(train_x, D_percent_drop)

        # Example usage
        # shuffled_train_x = shuffle_arrays(train_x)
        shuffled_train_x = reverse_arrays(train_x)

        print(f"\n Training the Siamese Multi-Headed Attention Neural Network (Encoder) - Train : {train} - Floorplan : {flp}\n")
        print("... \n")
        # Train the model with your data
        siamese_model.fit(
            x=[train_x, train_x_modified, shuffled_train_x, train_y],
            y=[train_y, train_y, train_y, train_y],
            batch_size=batchsize,
            epochs=epoch,
            verbose = 0
        )

        print("Encoding (STELLAR) Complete")
        print("\n Post Encoding Non-Parametric Model(s) ... \n")
        # Extract the encoded output for training data
        anchor_siamese_model = Model(siamese_model.input[0], siamese_model.output[-1])
        encoded_train_output = anchor_siamese_model.predict(train_x)
        # encoded_train_output_reshaped = []

        # Create and fit the KNN classifier
        knn_classifier = KNeighborsClassifier(n_neighbors=20)
        print('Training the KNN classifier')
        knn_classifier.fit(encoded_train_output, train_y)
        print("Training Complete")

        # Create and fit the Random Forest classifier
        random_forest_classifier = RandomForestClassifier(n_estimators=20)
        print('Training the RF classifier')
        random_forest_classifier.fit(encoded_train_output, train_y)
        print("Training Complete")

        # Create and fit the SVM classifier
        svm_classifier = svm.SVC(kernel='rbf')
        print('Training the SVM classifier')
        svm_classifier.fit(encoded_train_output, train_y)
        print("Training Complete")

        # Set the parameters for XGBoost
        params = {
            'objective': 'multi:softmax',
            'num_class': len(np.unique(train_y)),
            'max_depth': 2,
            'eta': 0.1,
            'subsample': 0.5,
            'colsample_bytree': 0.5
        }


        # Create the XGBoost classifier
        print('Training the XgBoost classifier')
        xgb_classifier = xgb.XGBClassifier(**params)
        print("Training Complete")

        # Train the XGBoost classifier
        xgb_classifier.fit(encoded_train_output, train_y)

        from catboost import CatBoostClassifier
        # Set the parameters for CatBoost
        params = {
            'iterations': 35,
            'learning_rate': 0.1,
            'depth': 6,
            'loss_function': 'MultiClass',
            'custom_metric': 'Accuracy',
            'random_seed': 42
        }

        # Create the CatBoost classifier
        print('Training the CatBoost classifier')
        catboost_classifier = CatBoostClassifier(**params)

        # Train the CatBoost classifier
        catboost_classifier.fit(encoded_train_output, train_y, verbose = 0)
        print("Training Complete")


        final_knn = []
        final_rf = []
        final_svm = []
        final_xgb = []
        final_ctb = []
        final_ngb = []

        for ci_val in range(int(ci_initial), int(ci_max)):
          for test_dev in dev:

              print("\n Testing ... \n")
              print(f'Test dev -> {test_dev}   flp -> {flp}  Ci -> {ci_val}')
              test_x, test_y = temp_test_data(train_aps, test_dev, flp, ci_val)
              prediction_model = Model(siamese_model.input[0], siamese_model.output[-1])

              pred = prediction_model.predict(test_x)

              predicted_labels_knn = knn_classifier.predict(pred)
              predicted_labels_rf = random_forest_classifier.predict(pred)
              predicted_labels_svm = svm_classifier.predict(pred)
              predicted_labels_xgb = xgb_classifier.predict(pred)
              predicted_labels_ctb = catboost_classifier.predict(pred)

              mean_error_knn = np.mean(np.abs(predicted_labels_knn - test_y))
              mean_error_rf = np.mean(np.abs(predicted_labels_rf - test_y))
              mean_error_svm = np.mean(np.abs(predicted_labels_svm - test_y))
              mean_error_xgb = np.mean(np.abs(predicted_labels_xgb - test_y))
              mean_error_ctb = np.mean(np.abs(predicted_labels_ctb - test_y))

              final_knn.append(mean_error_knn)
              final_rf.append(mean_error_rf)
              final_svm.append(mean_error_svm)
              final_xgb.append(mean_error_xgb)
              final_ctb.append(mean_error_ctb)

              print(f'Mean Error -> KNN {mean_error_knn} -> RF {mean_error_rf} -> SVM {mean_error_svm} -> XgB  {mean_error_xgb} -> CtB {mean_error_ctb}')
            # print(predicted_labels - test_y)
          print(f'Final Mean Error for: {flp} \n-> KNN {np.mean(final_knn)} \n-> RF {np.mean(final_rf)} \n-> SVM {np.mean(final_svm)} \n-> XgB  {np.mean(final_xgb)} \n-> CtB {np.mean(final_ctb)}')

# Author - Danish Gufran
# Danish.Gufran@colostate.edu

# Citation : https://ieeexplore.ieee.org/document/10323477

'''
STELLAR: Siamese Multi-Headed Attention Neural Networks for Overcoming
Temporal Variations and Device Heterogeneity
With Indoor Localization
'''

print(f'Final Mean Error for: {flp} \n-> KNN {np.mean(final_knn)} \n-> RF {np.mean(final_rf)} \n-> SVM {np.mean(final_svm)} \n-> XgB  {np.mean(final_xgb)} \n-> CtB {np.mean(final_ctb)}')

