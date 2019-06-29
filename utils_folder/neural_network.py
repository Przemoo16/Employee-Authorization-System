import tensorflow as tf
import numpy as np
import cv2
import h5py
import dlib
from .utils import extract_left_eye_center, extract_right_eye_center, get_rotation_matrix, crop_image

hdf = h5py.File('utils_folder/vgg_face_weights.h5', 'r')

conv1_1_W = np.array(hdf['conv1_1/conv1_1_2/kernel:0'])
conv1_1_B = np.array(hdf['conv1_1/conv1_1_2/bias:0'])

conv1_2_W = np.array(hdf['conv1_2/conv1_2_2/kernel:0'])
conv1_2_B = np.array(hdf['conv1_2/conv1_2_2/bias:0'])

conv2_1_W = np.array(hdf['conv2_1/conv2_1_2/kernel:0'])
conv2_1_B = np.array(hdf['conv2_1/conv2_1_2/bias:0'])

conv2_2_W = np.array(hdf['conv2_2/conv2_2_2/kernel:0'])
conv2_2_B = np.array(hdf['conv2_2/conv2_2_2/bias:0'])

conv3_1_W = np.array(hdf['conv3_1/conv3_1_1/kernel:0'])
conv3_1_B = np.array(hdf['conv3_1/conv3_1_1/bias:0'])

conv3_2_W = np.array(hdf['conv3_2/conv3_2_1/kernel:0'])
conv3_2_B = np.array(hdf['conv3_2/conv3_2_1/bias:0'])

conv3_3_W = np.array(hdf['conv3_3/conv3_3_1/kernel:0'])
conv3_3_B = np.array(hdf['conv3_3/conv3_3_1/bias:0'])

conv4_1_W = np.array(hdf['conv4_1/conv4_1_1/kernel:0'])
conv4_1_B = np.array(hdf['conv4_1/conv4_1_1/bias:0'])

conv4_2_W = np.array(hdf['conv4_2/conv4_2_1/kernel:0'])
conv4_2_B = np.array(hdf['conv4_2/conv4_2_1/bias:0'])

conv4_3_W = np.array(hdf['conv4_3/conv4_3_1/kernel:0'])
conv4_3_B = np.array(hdf['conv4_3/conv4_3_1/bias:0'])

conv5_1_W = np.array(hdf['conv5_1/conv5_1_1/kernel:0'])
conv5_1_B = np.array(hdf['conv5_1/conv5_1_1/bias:0'])

conv5_2_W = np.array(hdf['conv5_2/conv5_2_1/kernel:0'])
conv5_2_B = np.array(hdf['conv5_2/conv5_2_1/bias:0'])

conv5_3_W = np.array(hdf['conv5_3/conv5_3_1/kernel:0'])
conv5_3_B = np.array(hdf['conv5_3/conv5_3_1/bias:0'])

fc6_W = np.array(hdf['fc6/fc6_1/kernel:0'])
fc6_B = np.array(hdf['fc6/fc6_1/bias:0'])

fc7_W = np.array(hdf['fc7/fc7_1/kernel:0'])
fc7_B = np.array(hdf['fc7/fc7_1/bias:0'])

fc8_W = np.array(hdf['fc8/fc8_1/kernel:0'])
fc8_B = np.array(hdf['fc8/fc8_1/bias:0'])

# CONV2D


def conv2d(x, W, pad):
    # x --> [batch. H, W, Channels]
    # W --> [filter H, filter W, Channels IN, Channels OUT]

    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding=pad)

# POOLING


def max_pool_2by2(x):
    # x --> [batch. H, W, Channels]

    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

# CONVOLUTIONAL LAYER


def convolutional_layer(input_x, shape, W, b, pad, activation):
    if activation == 'relu':
        return tf.nn.relu(conv2d(input_x, W, pad)+b)
    elif activation is None:
        return conv2d(input_x, W, pad)+b


def create_model():
    g = tf.Graph()
    with g.as_default():
        x = tf.placeholder(tf.float32, shape=(1, 224, 224, 3), name='x')
        conv1_1 = convolutional_layer(x, [3, 3, 3, 64], conv1_1_W, conv1_1_B, 'SAME', 'relu')
        conv1_2 = convolutional_layer(conv1_1, [3, 3, 64, 64], conv1_2_W, conv1_2_B, 'SAME', 'relu')
        conv1_pooling = max_pool_2by2(conv1_2)

        conv2_1 = convolutional_layer(
            conv1_pooling, [3, 3, 64, 128], conv2_1_W, conv2_1_B, 'SAME', 'relu')
        conv2_2 = convolutional_layer(
            conv2_1, [3, 3, 128, 128], conv2_2_W, conv2_2_B, 'SAME', 'relu')
        conv2_pooling = max_pool_2by2(conv2_2)

        conv3_1 = convolutional_layer(
            conv2_pooling, [3, 3, 128, 256], conv3_1_W, conv3_1_B, 'SAME', 'relu')
        conv3_2 = convolutional_layer(
            conv3_1, [3, 3, 256, 256], conv3_2_W, conv3_2_B, 'SAME', 'relu')
        conv3_3 = convolutional_layer(
            conv3_2, [3, 3, 256, 256], conv3_3_W, conv3_3_B, 'SAME', 'relu')
        conv3_pooling = max_pool_2by2(conv3_3)

        conv4_1 = convolutional_layer(
            conv3_pooling, [3, 3, 256, 512], conv4_1_W, conv4_1_B, 'SAME', 'relu')
        conv4_2 = convolutional_layer(
            conv4_1, [3, 3, 512, 512], conv4_2_W, conv4_2_B, 'SAME', 'relu')
        conv4_3 = convolutional_layer(
            conv4_2, [3, 3, 512, 512], conv4_3_W, conv4_3_B, 'SAME', 'relu')
        conv4_pooling = max_pool_2by2(conv4_3)

        conv5_1 = convolutional_layer(
            conv4_pooling, [3, 3, 512, 512], conv5_1_W, conv5_1_B, 'SAME', 'relu')
        conv5_2 = convolutional_layer(
            conv5_1, [3, 3, 512, 512], conv5_2_W, conv5_2_B, 'SAME', 'relu')
        conv5_3 = convolutional_layer(
            conv5_2, [3, 3, 512, 512], conv5_3_W, conv5_3_B, 'SAME', 'relu')
        conv5_pooling = max_pool_2by2(conv5_3)

        fc6 = convolutional_layer(conv5_pooling, [7, 7, 512, 4096], fc6_W, fc6_B, 'VALID', 'relu')
        # fc6_dropout = tf.nn.dropout(fc6, 0.5, seed=123)
        fc7 = convolutional_layer(fc6, [1, 1, 4096, 4096], fc7_W, fc7_B, 'VALID', 'relu')
        # fc7_dropout = tf.nn.dropout(fc7, 0.5, seed=123)
        fc8 = convolutional_layer(fc7, [1, 1, 4096, 2622], fc8_W, fc8_B, 'VALID', None)

        flatten = tf.reshape(fc8, (-1,), name='flatten')

        return g


def crop_face(input_image):

    img = cv2.imread(input_image, cv2.IMREAD_COLOR)
    height, width = img.shape[:2]

    dets = detector(img, 1)

    if dets:

        det = dets[0]

        shape = predictor(img, det)
        left_eye = extract_left_eye_center(shape)
        right_eye = extract_right_eye_center(shape)

        M = get_rotation_matrix(left_eye, right_eye)
        rotated = cv2.warpAffine(img, M, (width, height), flags=cv2.INTER_CUBIC)

        cropped = crop_image(rotated, det)

        cropped = cv2.resize(cropped, (224, 224))

        cropped = np.expand_dims(cropped, axis=0)

        return cropped

    else:
        img_normal = cv2.resize(img, (224, 224))
        img_normal = np.expand_dims(img_normal, axis=0)
        return img_normal


def findCosineSimilarity(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))


def findEuclideanDistance(source_representation, test_representation):
    euclidean_distance = source_representation - test_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)
    return euclidean_distance


def crop_cam(img):

    height, width = img.shape[:2]

    dets = detector(img, 1)

    if dets:
        det = dets[0]

        shape = predictor(img, det)
        left_eye = extract_left_eye_center(shape)
        right_eye = extract_right_eye_center(shape)

        M = get_rotation_matrix(left_eye, right_eye)
        rotated = cv2.warpAffine(img, M, (width, height), flags=cv2.INTER_CUBIC)

        cropped = crop_image(rotated, det)

        cropped = cv2.resize(cropped, (224, 224))
        cropped = np.expand_dims(cropped, axis=0)

        return cropped
    else:
        img_normal = cv2.resize(img, (224, 224))
        img_normal = np.expand_dims(img_normal, axis=0)
        return img_normal


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("utils_folder/shape_predictor_68_face_landmarks.dat")

person = 0

graph = create_model()

epsilon = 0.25

sess = tf.Session(graph=graph)

img_rep = []

img1 = crop_face('utils_folder/rec_images/me.png')

img_representation = np.array(sess.run(['flatten:0'], feed_dict={'x:0': img1}))
img_representation = np.reshape(img_representation, (-1,))

img_rep.append(img_representation)

print('-----------------')
print('READY')
print('-----------------')


def original_images(face):

    print('-----------------')
    print('LOAD NEW FACE')
    print('-----------------')

    global img_rep

    cropped_face = crop_cam(face)

    img_representation = np.array(sess.run(['flatten:0'], feed_dict={'x:0': cropped_face}))
    img_representation = np.reshape(img_representation, (-1,))

    img_rep.append(img_representation)

    print('-----------------')
    print('READY')
    print('-----------------')


def face_reg(frame_start):

    global person

    frame_end = crop_cam(frame_start)

    frame_representation = np.array(sess.run(['flatten:0'], feed_dict={'x:0': frame_end}))
    frame_representation = np.reshape(frame_representation, (-1,))

    similarity_tab = []

    for image in img_rep:

        cosine_similarity = findCosineSimilarity(image, frame_representation)
        similarity_tab.append(cosine_similarity)

    if (np.min(similarity_tab) < epsilon):
        person = np.argmin(similarity_tab) + 1
    else:
        person = 0
