# Based on: https://github.com/yu4u/age-gender-estimation/tree/de397adac1505c479c092e3422ad4f8f74e52555
from pathlib import Path
from wide_resnet import WideResNet
from keras.utils.data_utils import get_file
import numpy as np
import cv2
import dlib
import tensorflow as tf

# model source: https://github.com/yu4u/age-gender-estimation
pretrained_model = "https://github.com/yu4u/age-gender-estimation/releases/download/v0.5/weights.28-3.73.hdf5"
modhash = 'fbe63257a054c1c5466cfd7bf14646d6'

img_size = 64

# for face detection
detector = dlib.get_frontal_face_detector()

# create model and load weights
weight_file = get_file("weights.28-3.73.hdf5", pretrained_model, cache_subdir="models",
                       file_hash=modhash, cache_dir=str(Path(__file__).resolve().parent))
depth = 16
k = 8
model = WideResNet(img_size, depth=depth, k=k)()
model.load_weights(weight_file)

graph = tf.get_default_graph()


def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
               font_scale=0.8, thickness=1):
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x, y = point
    cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)


def get_gender_and_age(image_path):
    margin = 0.4
    out = {
        "image": None,
        "faces": [],
        "results": []
    }

    # resize image
    img_orig = cv2.imread(image_path, 1)
    h, w, _ = img_orig.shape
    r = 640 / max(w, h)
    img = cv2.resize(img_orig, (int(w * r), int(h * r)))

    # prepare input
    input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_h, img_w, _ = np.shape(input_img)

    # get face by dlib
    detected = detector(input_img, 1)
    faces = np.empty((len(detected), img_size, img_size, 3))

    if len(detected) > 0:
        for i, d in enumerate(detected):
            x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
            xw1 = max(int(x1 - margin * w), 0)
            yw1 = max(int(y1 - margin * h), 0)
            xw2 = min(int(x2 + margin * w), img_w - 1)
            yw2 = min(int(y2 + margin * h), img_h - 1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
            faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))
            # format for PIL.ImageDraw.Draw.rectangle
            out['faces'].append((int(x1 / r), int(y1 / r), int(x2 / r), int(y2 / r)))
            # cv2.rectangle(img_orig, (out['faces'][i]['x1'], out['faces'][i]['y1']), (out['faces'][i]['x2'], out['faces'][i]['y2']), (255, 0, 0), 2)

        # predict ages and genders of the detected faces
        results = predict(faces)
        predicted_genders = results[0]
        ages = np.arange(0, 101).reshape(101, 1)
        predicted_ages = results[1].dot(ages).flatten()

        # prepare results
        for i, d in enumerate(detected):
            label = "{}, {}".format(int(predicted_ages[i]),
                                    "M" if predicted_genders[i][0] < 0.5 else "F")
            draw_label(img, (d.left(), d.bottom()), label)

            out['results'].append({
                "age": int(predicted_ages[i]),
                "gender": 0 if predicted_genders[i][0] < 0.5 else 1,
                "gender_label": "Male" if predicted_genders[i][0] < 0.5 else "Female",
                "gender_predict": float(predicted_genders[i][0])
            })

        # face with label now in in img
        _, buffer = cv2.imencode('.jpg', img)
        out['image'] = buffer

    return out


def predict(inp):
    # simple hack for flask threads in dev mode
    # https://stackoverflow.com/questions/51127344/tensor-is-not-an-element-of-this-graph-deploying-keras-model
    global graph
    with graph.as_default():
        return model.predict(inp)


if __name__ == '__main__':
    out = get_gender_and_age("fixtures/putin.jpg")
    print(out)
