from odf.sabotage import all_attacks
from odf.components import Command, Data, Status, Word

import tensorflow as tf
from tensorflow.keras.losses import sparse_categorical_crossentropy
from tensorflow.keras.metrics import sparse_categorical_accuracy


def word2seq(t: int, w: Word):
    def _inner():
        if isinstance(w, Data):
            return list(w.data)
        if isinstance(w, Command):
            return [w.address, w.tr, w.sub_address, w.dword_count]
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


# all_attacks defined in odf package
total_attacks = len(all_attacks) + 1


def attk2index(attk):
    # string to attack index
    for i, a in enumerate(all_attacks):
        if a.__name__ == attk:
            return i+1
    return 0


def file2sample(session, size=5):
    words = [word2seq(*d) for d in session['data']]
    windows = []
    for i in range(len(words)):
        win = words[max(0, i-size+1):i+1]
        x = [i for w in win for i in w[0]]
        y = [w[1] for w in win]
        if len(win) == size:
            # (sequence, label, type)
            windows.append(
                (x, 1 if any(y) else 0, attk2index(session['attack_types'][0] if any(y) else 'NA')))
    return windows


def lossIgnoreBenign(yTrue, yPred):
    mask = tf.squeeze(tf.greater(yTrue, 0), 1)
    yTrue = tf.boolean_mask(yTrue, mask)
    yPred = tf.boolean_mask(yPred, mask)
    return sparse_categorical_crossentropy(yTrue, yPred)


def accIgnoreBenign(yTrue, yPred):
    mask = tf.squeeze(tf.greater(yTrue, 0), 1)
    yTrue = tf.boolean_mask(yTrue, mask)
    yPred = tf.boolean_mask(yPred, mask)
    return sparse_categorical_accuracy(yTrue, yPred)

def passthrough(y_true, y_pred):
    return tf.reduce_mean(y_pred)