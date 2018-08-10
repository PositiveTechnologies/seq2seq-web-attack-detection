from __future__ import print_function
import random
import numpy as np

from sklearn.model_selection import train_test_split

from vocab import Vocabulary
from utils import get_requests_from_file, batch_generator, one_by_one_generator


class Reader(object):

    def __init__(self, data_path, vocab=Vocabulary()):
        self.vocab = vocab

        data = get_requests_from_file(data_path)
        print("Downloaded {} samples".format(len(data)))

        map_result = map(self._process_request, data)
        self.data = [x[0] for x in map_result]
        self.lengths = [x[1] for x in map_result]
        assert len(self.data) == len(self.lengths)

    def _process_request(self, req):
        """
        Splits a request into lines and convert a string into ints.
        """
        seq = self.vocab.string_to_int(req)
        l = len(seq)

        return seq, l


class Data(Reader):

    def __init__(self, data_path, vocab=Vocabulary(), predict=False):
        """
        Creates an object that gets data from a file.
        """
        super(Data, self).__init__(data_path, vocab)

        if not predict:
            self._train_test_split()

    def _train_test_split(self):
        """
        Train/val/test split for anomaly detection problem.
        """
        # Shuffle requests
        data, lengths = self._shuffle(self.data, self.lengths)

        # Split into train/val/test
        X_train, X_test, l_train, l_test = train_test_split(data, lengths, test_size=0.1)
        X_train, X_val, l_train, l_val = train_test_split(X_train, l_train, test_size=0.2)

        self.X_train, self.l_train = X_train, l_train
        self.X_val, self.l_val = X_val, l_val
        self.X_test, self.l_test = X_test, l_test

        self.train_size = len(X_train)
        self.val_size = len(X_val)
        self.test_size = len(X_test)

    def _shuffle(self, data, lengths):
        temp = list(zip(data, lengths))
        random.shuffle(temp)
        data, lengths = zip(*temp)
        
        return data, lengths

    def train_generator(self, batch_size, num_epochs):
        return batch_generator(
            self.X_train,
            self.l_train,
            num_epochs,
            batch_size,
            self.vocab)

    def val_generator(self):
        return one_by_one_generator(
            self.X_val,
            self.l_val,
            self.vocab)

    def test_generator(self):
        return one_by_one_generator(
            self.X_test,
            self.l_test,
            self.vocab)

    def predict_generator(self):
        return one_by_one_generator(
            self.data,
            self.lengths,
            self.vocab)
