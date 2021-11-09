# IMPORTS
import os
import numpy as np
import pandas as pd
import logging as log

# OD1NF1ST IMPORTS
from odf.components import Word
from odf.ids.ids_utils import *
from odf.ids.defines import IDS
from odf.sabotage import all_attacks

# ML IMPORTS
import tensorflow as tf
from tensorflow.keras.callbacks import (EarlyStopping, LambdaCallback,
                                        ModelCheckpoint)
from tensorflow.keras.layers import (Conv1D, Dense, Dropout, Embedding,
                                     Flatten, GlobalMaxPooling1D, Input,
                                     Multiply, Bidirectional, LSTM)
from tensorflow.keras.preprocessing.sequence import pad_sequences


class OD1N(IDS):

    def __init__(self, embedding_size=8, window_size=5, topk=25) -> None:
        super().__init__()
        self.embedding_size = embedding_size
        self.model_train = None
        self.model_infer = None
        self.sequence_buffer = []
        self.label_buffer = []
        self.window_size = window_size
        self.topk = topk

    def _build(self):
        input_dim = 256 
        topk = self.topk
        padding_char = 256
        embedding_size = self.embedding_size

        inp = Input(batch_shape=(None, None,), dtype='int64')
        emb = Embedding(input_dim, embedding_size)(inp)
        # attn = Conv1D(filters=1, kernel_size=3, strides=1, use_bias=True, activation='sigmoid', padding='valid')(emb)
        scores = Conv1D(filters=1, kernel_size=3, strides=1, use_bias=True, activation='softmax', padding='valid')(emb)
        
        
        # making batch * seq number of decisions
        # (these decisions are independent)
        # give reward based on the consequence of decision: 
        #    if prediction is correct: reward 1
        #    if prediction is incorrect: reward 0
        # loss value (REINFORCE Alorightm): log_prob * reward
          
        scores = tf.squeeze(scores, -1)
        # [batch, seq] in [0, 1]
        
        indices = tf.math.top_k(scores, k=topk, sorted=False).indices
        indices = tf.sort(indices, axis=-1)
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
            loss=['binary_crossentropy', passthrough, passthrough],
            optimizer='adam',
            metrics=[['binary_accuracy', 'AUC', 'Precision', 'Recall'], [None], [None]]
        )

        model_infer = tf.keras.Model(inp, (out_anomaly, out_misuse))
        return model_train, model_infer

    def prepare(self):
        self.prepared = True
        self.model_train, self.model_infer = self._build()
        model_file = os.path.join(self.get_model_path(), 'checkpoint')
        history_file = os.path.join(self.get_model_path(), 'histroy.csv')

        data = self.get_prepared_data()
        ds = [s for d in data for s in file2sample(d, size=self.window_size)]
        x = pad_sequences([d[0] for d in ds], padding='post')
        y = np.array([d[1] for d in ds])
        z = np.array([d[2] for d in ds])

        if os.path.exists(model_file):
            log.info(f'loading trained model from {model_file}')
            self.model_train.load_weights(model_file)
            return
        log.info('training the model..')



        mcp_save = ModelCheckpoint(
            model_file,
            save_best_only=True,
            save_weights_only=True,
            monitor='val_anomaly_auc',
            mode='max')

        # 50% training data, set verbose=1 to show training progress
        history = self.model_train.fit((x, y), (y, z, y), validation_split=0.50, epochs=20, batch_size=1024, verbose=2, callbacks=[mcp_save]) 
        pd.DataFrame(history.history).to_csv(history_file)
        self.model_train.load_weights(model_file)

    def monitor(self, t: int, word: Word):

        seq = word2seq(t, word)  # not taking the faked label

        self.sequence_buffer.append(seq[0])
        self.label_buffer.append(seq[1])
        if len(self.sequence_buffer) > self.window_size:
            self.sequence_buffer = self.sequence_buffer[1:]
            self.label_buffer = self.label_buffer[1:]
        if len(self.sequence_buffer) < self.window_size:
            return 0, [0] * len(all_attacks)


        # flatten out sequence
        # need to pad so topk selection works (if sequence is too short will crash)

        x = pad_sequences(self.sequence_buffer, maxlen=self.topk+5, padding='post')
        y = np.array(self.label_buffer).astype(int)

        anomaly, attks, reinforce = self.model_train((x, y))
        return anomaly.numpy().tolist()[0][0], attks.numpy()[0][1:].tolist()


class GCNN(IDS):

    def __init__(self, embedding_size=8, window_size=5) -> None:
        super().__init__()
        self.embedding_size = embedding_size
        self.model = None
        self.buffer = []
        self.window_size = window_size

    def _build(self):
        input_dim = 256  # maximum integer
        inp = Input(shape=(None,), dtype='int64')
        emb = Embedding(input_dim, self.embedding_size)(inp)
        filt = Conv1D(filters=128, kernel_size=3, strides=1,
                      use_bias=True, activation='relu', padding='valid')(emb)
        attn = Conv1D(filters=128, kernel_size=3, strides=1,
                      use_bias=True, activation='sigmoid', padding='valid')(emb)
        gated = Multiply()([filt, attn])
        feat = GlobalMaxPooling1D()(gated)
        dense = Dense(128, activation='relu')(feat)
        out_anomaly = Dense(1, activation='sigmoid', name='anomaly')(dense)
        out_misuse = Dense(
            total_attacks, activation='softmax', name='misuse')(dense)

        model = tf.keras.Model(inp, (out_anomaly, out_misuse))
        model.compile(
            loss=['binary_crossentropy', lossIgnoreBenign],
            optimizer='adam',
            metrics=[['binary_accuracy', 'AUC', 'Precision',
                      'Recall'], [accIgnoreBenign]]
        )
        return model
        
    def prepare(self):
        self.prepared = True
        self.model = self._build()
        model_file = os.path.join(self.get_model_path(), 'checkpoint')
        history_file = os.path.join(self.get_model_path(), 'histroy.csv')

        if os.path.exists(model_file):
            log.info(f'loading trained model from {model_file}')
            self.model.load_weights(model_file)
            return
        log.info('training the model..')

        data = self.get_prepared_data()
        ds = [s for d in data for s in file2sample(d, size=self.window_size)]
        x = pad_sequences([d[0] for d in ds], padding='post')
        y = np.array([d[1] for d in ds])
        z = np.array([d[2] for d in ds])

        mcp_save = ModelCheckpoint(
            model_file,
            save_best_only=True,
            save_weights_only=True,
            monitor='val_anomaly_auc',
            mode='max')

        # 50% training data, set verbose=1 to show training progress
        history = self.model.fit(
            x, (y, z), validation_split=0.50,
            epochs=60, batch_size=1024, verbose=2, callbacks=[mcp_save])
        pd.DataFrame(history.history).to_csv(
            history_file
        )
        self.model.load_weights(model_file)
    
    def monitor(self, t: int, word: Word):
        seq = word2seq(t, word)[0]  # not taking the faked label
        self.buffer.append(seq)
        if len(self.buffer) > self.window_size:
            self.buffer = self.buffer[1:]
        if len(self.buffer) < self.window_size:
            return 0, [0] * len(all_attacks)

        # flatten out sequence
        win = np.array([[i for s in self.buffer for i in s]])
        anomaly, attks = self.model(win)
        return anomaly.numpy().tolist()[0][0], attks.numpy()[0][1:].tolist()


