#!/usr/bin/env python
# coding: utf-8

# In[1]:


from odf import *
import numpy as np
import tensorflow as tf
import keras
from tensorflow.keras.layers import (GlobalMaxPooling1D, Multiply, Conv1D, Dense, Input, Embedding, LSTM, Bidirectional)


# In[2]:


with open('saved_model/x.npy', 'rb') as f:
    x = np.load(f)
with open('saved_model/y.npy', 'rb') as f:
    y = np.load(f)
with open('saved_model/z.npy', 'rb') as f:
    z = np.load(f)


# In[3]:


# OD1NF1ST

# MALCONV + OD1NF1ST

def passthrough(y_true, y_pred):
    return tf.reduce_mean(y_pred)

def build(topk=25):
    input_dim = 256 # maximum integer 
    padding_char = 256
    embedding_size = 8 

    inp = Input(batch_shape=(None, None,), dtype='int64')
    emb = Embedding( input_dim, embedding_size)(inp)
    # attn = Conv1D( filters=1, kernel_size=3, strides=1, use_bias=True, activation='sigmoid', padding='valid')(emb)
    scores = Conv1D( filters=1, kernel_size=3, strides=1, use_bias=True, activation='softmax', padding='valid')(emb)
    
    
    # making batch * seq number of decisions (these decisions are independent)
    # give reward based on the consequence of decision: 
    #    if prediction is correct: reward 1
    #    if prediction is incorrect: reward 0
    # loss value (REINFORCE Alorightm): log_prob * reward
    # 
    
    scores = tf.squeeze(scores, -1)
    # [batch, seq] in [0, 1]
    
    indices = tf.math.top_k(scores, k=topk, sorted=False).indices
    indices = tf.sort(indices, axis=-1)
    print(indices)
    selected = tf.gather(emb, indices, batch_dims=1)
    
    
    
    filt = Conv1D( filters=128, kernel_size=3, strides=1, use_bias=True, activation='relu', padding='valid' )(selected)
    attn = Conv1D( filters=128, kernel_size=3, strides=1, use_bias=True, activation='sigmoid', padding='valid')(selected)
    gated = Multiply()([filt,attn])
    feat = GlobalMaxPooling1D()( gated )
    dense = Dense(128, activation='relu')(feat)
    out_anomaly = Dense(1, activation='sigmoid', name='anomaly')(dense)
    out_misuse = Dense(11, activation='softmax', name='misuse')(dense)

    
    
    truth_anomaly = Input(batch_shape=(None,), dtype='int64')
    reward = tf.cast(tf.equal(tf.cast(tf.round(out_anomaly), 'int64'), truth_anomaly), 'float32')
    # [batch, ]
    loss_reinforce = tf.math.log(scores) * tf.expand_dims(reward, -1) * 0.5
    # [batch, 1]
    
    model_train = tf.keras.Model((inp, truth_anomaly), (out_anomaly, out_misuse, loss_reinforce))
    model_train.compile(
        loss=['binary_crossentropy', 'sparse_categorical_crossentropy', passthrough ], 
        optimizer='adam',
        metrics=[['binary_accuracy', 'AUC', 'Precision', 'Recall'], ['sparse_categorical_accuracy'], [None]]
    )
    
 
    model_infer = tf.keras.Model(inp, (out_anomaly, out_misuse))
    return model_train, model_infer

model_train, model_infer = build()


# In[4]:


checkpoint_path = "saved_model/cp.ckpt"
model_train.load_weights(checkpoint_path)


# In[5]:


start = time.time()
history = model_train.evaluate((x, y), (y, z, y), verbose=1)
end = time.time()

print("Runtime: " + str(end - start) + "s")