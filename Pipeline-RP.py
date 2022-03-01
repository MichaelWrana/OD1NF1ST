#!/usr/bin/env python
# coding: utf-8

# In[1]:


from odf import *
from pathlib import Path
from tqdm.notebook import tqdm
import numpy as np
import random
import tensorflow as tf
import keras
from tensorflow.keras.layers import (Conv1D, Flatten, Dense, 
                                     Dropout, Input, Multiply, 
                                     Embedding, GlobalMaxPooling1D,
                                     LSTM, RepeatVector,GRU, SimpleRNN, Bidirectional)
from tensorflow.keras.layers import Layer, GRUCell, GRU, RNN, Flatten, LSTMCell
from tensorflow.python.keras.layers.recurrent import _generate_zero_filled_state_for_cell


# In[2]:


# load JSON from 'data' folder into python array
folder = 'datasmall'
data = [
    jsonpickle.decode(
    Path(os.path.join(folder, f)).read_text()
    ) for f in tqdm(os.listdir(folder))]


# In[3]:


'''
converts a word sent over the bus into its component parts
returns: an array containing an integer representing each piece of the message, the class (attack type) label
'''
def word2seq(t:int, w: Word):
    def _inner():
        if isinstance(w, Data):
            return list(w.data)
        if isinstance(w, Command):
            return [
                w.address, 
                w.tr, 
                w.sub_address, 
                w.dword_count
            ]
        if isinstance(w, Status):
            return [
                w.address, 
                w.message_error_bit, 
                w.instrumentation_bit, 
                w.service_request_bit,
                w.reserved_bits,
                w.brdcst_received_bit,
                w.busy_bit,
                w.subsystem_flag_bit,
                w.dynamic_bus_control_accpt_bit,
                w.terminal_flag_bit,
                w.parity_bit,
            ]    
    return [int(i) for i in _inner()], w.fake


# In[4]:


# all_attacks defined in odf package
total_attacks = len(all_attacks) + 1 

# convert the attack type listed into an integer (for classification)
def attk2index(attk):
    # string to attack index
    for i, a in enumerate(all_attacks):
        if a.__name__ == attk:
            return i+1
    return 0

'''
Converts the raw JSON file into data format which can be interpreted by the network
Inputs
    session: array of arrays containing [[timestamp, word]...] for each message
    size: maximum allowed sequence length in number of words
Output:
    array of tuples containing: (sequence, attack label (T/F), attack type)
'''
def file2sample(session, size=5):
    # load the words sent over the bus
    words = [word2seq(*d) for d in session['data']]
    attack_count = 0
    benign_count = 0

    # empty output array
    windows = []
    # loop through each word sent on the bus
    for i in range(len(words)):
        # get a sequence of command words from the overall list (depending on size)
        win = words[max(0, i-size+1):i+1]
        # extract the sequence of information being sent in the word
        x = [i for w in win for i in w[0]]
        # extract the class label for each word
        y = [w[1] for w in win]
        if len(win) == size:
            # append (sequence, label, type) to output array
            # check if any of the commands that were part of the sequence are malicious
            # if so, label the whole sequence as malicious
            # also determine specifically which type of attack is occuring
            
            windows.append((x, 1 if any(y) else 0, attk2index(session['attack_types'][0] if any(y) else 'NA')))
            
            # Select specific attack types (for cross-validation) from this list:
            # ['No_attack','Collision_Attack_against_the_Bus','Desynchronization_Attack_on_RT'
            #,'Collision_Attack_against_an_RT','Data_Corruption_Attack','Fake_Status_trcmd',
            # 'Shutdown_Attack_on_RT','Fake_Status_reccmd','Data_Thrashing_Attack_against_an_RT'
            # ,'MITM_attack_on_RTs','Command_Invalidation_Attack']
            '''
            if(any(y)):
                if(session['attack_types'][0] == "Desynchronization_Attack_on_RT"):
                    windows.append((x, 1, attk2index(session['attack_types'][0])))
                    attack_count += 1
            elif(random.random() > 0.9):
                windows.append((x, 0,'NA'))
                benign_count += 1
            '''
            
    return windows


# In[5]:


totalwords = 0;
attacktypes = ['No_attack','Collision_Attack_against_the_Bus','Desynchronization_Attack_on_RT','Collision_Attack_against_an_RT','Data_Corruption_Attack','Fake_Status_trcmd', 'Shutdown_Attack_on_RT','Fake_Status_reccmd','Data_Thrashing_Attack_against_an_RT','MITM_attack_on_RTs','Command_Invalidation_Attack']
attackpresence = dict.fromkeys(attacktypes, 0)

for d in tqdm(data):
    totalwords += len(d['data'])
    try:
        attackpresence[d['attack_types'][0]] = attackpresence.get(d['attack_types'][0]) + len(d['attack_times'][0])
    except:
        pass
    
print(attackpresence)
print(sum(attackpresence.values()))
print(totalwords)


# In[6]:


from tensorflow.keras.preprocessing.sequence import pad_sequences

# window size
max_win = 10

ds = [s for d in tqdm(data) for s in file2sample(d, size=max_win)]
# the sequences need to be padded so the length matches
# problem: each sequence has a different length depending on type of word (data, status, command)
x = pad_sequences([d[0] for d in ds], padding='post',)

print(len(x))
# convert class into numpy array
y = np.array([d[1] for d in ds])
# convert attack type into numpy array
z = np.array([d[2] for d in ds])


# In[7]:


# important note: each one has a different number of data points associated depending on the type of word
# so the padding is weird

for i in range(1):
    # (sequence, anomaly label, attack class)
    print(x[i], y[i], z[i])
    
print(len(x[0]))


# In[ ]:


# OD1NF1ST

def passthrough(y_true, y_pred):
    return tf.reduce_mean(y_pred)

def build2(topk=25):
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
    
    
    
    z0 = Bidirectional(LSTM(32, return_sequences=True))(selected)
    z1 = Bidirectional(LSTM(128))(z0)
    
    dense = Dense(128, activation='relu')(z1)
    
    out_anomaly = Dense(1, activation='sigmoid', name='anomaly')(dense)
    out_misuse = Dense(11, activation='softmax', name='misuse')(dense)
    
    
    truth_anomaly = Input(batch_shape=(None,), dtype='int64')
    reward = tf.cast(tf.equal(tf.cast(tf.round(out_anomaly), 'int64'), truth_anomaly), 'float32')
    # [batch, ]
    loss_reinforce = tf.math.log(scores) * tf.expand_dims(reward, -1) * 1.0
    # [batch, 1]
    
    model_train = tf.keras.Model((inp, truth_anomaly), (out_anomaly, out_misuse, loss_reinforce))
    model_train.compile(
        loss=['binary_crossentropy', passthrough, passthrough ], 
        optimizer='adam',
        metrics=[['binary_accuracy', 'AUC', 'Precision', 'Recall'], ['sparse_categorical_accuracy'], [None]]
    )
    
 
    model_infer = tf.keras.Model(inp, (out_anomaly, out_misuse))
    return model_train, model_infer

model_train, model_infer = build2()

model_train.summary()


# In[ ]:



start = time.time()
history = model_train.fit((x, y), (y, z, y), validation_split=0.9, epochs=15, batch_size=1024, verbose=1)
#history = model.fit(x, (y, z), validation_split=0.90, epochs=15, batch_size=1024, verbose=1) 
end = time.time()



# In[ ]:


# final performance 

precision = history.history['val_anomaly_precision'][-1]
recall = history.history['val_anomaly_recall'][-1]

print("Precision: " + str(history.history['val_anomaly_precision'][-1]))
print("Recall: " + str(history.history['val_anomaly_recall'][-1]))
print("F1: " + str(2 * ((precision*recall)/(precision+recall))))
print("AUC: " + str(history.history['val_anomaly_auc'][-1]))
print("SCA: " +  str(history.history['val_misuse_sparse_categorical_accuracy'][-1]))
print("Runtime: " + str(end - start) + "s")

