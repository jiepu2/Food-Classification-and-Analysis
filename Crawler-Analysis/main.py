from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy as np
import os
import keras
import h5py
from scipy.misc import imresize
import matplotlib.pyplot as plt
from keras.applications.inception_v3 import preprocess_input, decode_predictions
import collections
import urllib
from skimage import io

class_to_ix = {}
ix_to_class = {}
with open('classes.txt', 'r') as txt:
    classes = [l.strip() for l in txt.readlines()]
    class_to_ix = dict(zip(classes, range(len(classes))))
    ix_to_class = dict(zip(range(len(classes)), classes))
    class_to_ix = {v: k for k, v in ix_to_class.items()}
sorted_class_to_ix = collections.OrderedDict(sorted(class_to_ix.items()))

print(keras.__version__)
np.random.seed(7)

json_file = open('foodRec.json', 'r')
loaded_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_json)

loaded_model.load_weights("foodRec.hdf5")
print("Model Loaded!")

print("Loading Image")

def center_crop(x, center_crop_size, **kwargs):
    centerw, centerh = x.shape[0]//2, x.shape[1]//2
    halfw, halfh = center_crop_size[0]//2, center_crop_size[1]//2
    return x[centerw-halfw:centerw+halfw+1,centerh-halfh:centerh+halfh+1, :]

def predict_10_crop(img, ix, top_n=5, plot=False, preprocess=True, debug=False):
    flipped_X = np.fliplr(img)
    crops = [
        img[:299, :299, :],  # Upper Left
        img[:299, img.shape[1] - 299:, :],  # Upper Right
        img[img.shape[0] - 299:, :299, :],  # Lower Left
        img[img.shape[0] - 299:, img.shape[1] - 299:, :],  # Lower Right
        center_crop(img, (299, 299)),

        flipped_X[:299, :299, :],
        flipped_X[:299, flipped_X.shape[1] - 299:, :],
        flipped_X[flipped_X.shape[0] - 299:, :299, :],
        flipped_X[flipped_X.shape[0] - 299:, flipped_X.shape[1] - 299:, :],
        center_crop(flipped_X, (299, 299))
    ]
    if preprocess:
        crops = [preprocess_input(x.astype('float32')) for x in crops]

    if plot:
        fig, ax = plt.subplots(2, 5, figsize=(10, 4))
        ax[0][0].imshow(crops[0])
        ax[0][1].imshow(crops[1])
        ax[0][2].imshow(crops[2])
        ax[0][3].imshow(crops[3])
        ax[0][4].imshow(crops[4])
        ax[1][0].imshow(crops[5])
        ax[1][1].imshow(crops[6])
        ax[1][2].imshow(crops[7])
        ax[1][3].imshow(crops[8])
        ax[1][4].imshow(crops[9])

    y_pred = loaded_model.predict(np.array(crops))
    preds = np.argmax(y_pred, axis=1)
    top_n_preds = np.argpartition(y_pred, -top_n)[:, -top_n:]
    if debug:
        print('Top-1 Predicted:', preds)
        print('Top-5 Predicted:', top_n_preds)
    return preds, top_n_preds

# predict_10_crop('0.jpg')
