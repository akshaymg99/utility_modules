import requests
import json
import base64
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
import matplotlib.pyplot as plt
import cv2
import numpy as np

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from numpy import dot
from numpy.linalg import norm


def get_image_pil_object_from_image_url(image_url):
    req = urlopen(image_url, timeout=8).read()
    img_pil_obj = Image.open(BytesIO(bytearray(req)))
    return img_pil_obj

def get_image_pil_object_from_image_path(image_path):
    img_pil_obj = Image.open(image_path)
    return img_pil_obj

def get_base46_from_img_url(image_url):
    img_pil_obj = get_image_pil_object_from_image_url(image_url)
    buffered = BytesIO()
    img_pil_obj.save(buffered, format="JPEG")
    base64_encoded_img = base64.b64encode(buffered.getvalue()).decode()
    return base64_encoded_img


def get_text_from_image(image_filepath, read_type):
    """
    image_filepath : path of local image file to extract text from (supports multiple image formats)
    returns extracted text in string format
    """
    VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate"
    API_KEY = "AIzaSyCKxG4fDqutQLPJ8QMvioF8PDRGz2ESPyQ"
    extracted_text = ""
    bounding_box = None
    try:
        if read_type == "image":
            # encode image into base64 format
            base64_encoded_img = None
            with open(image_filepath, 'rb') as image_file:
                base64_encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
        elif read_type == "url":
            base64_encoded_img = get_base46_from_img_url(image_filepath)
        else:
            return ""

        payload = {'requests': [{'image': {'content': base64_encoded_img}, 'features': [{'type': 'TEXT_DETECTION'}]}]}
        response = requests.post("{}?key={}".format(VISION_API_URL, API_KEY), json=payload)
        response_data = json.loads(response.text)
        text_ext = response_data['responses'][0]['textAnnotations']
        extracted_text = text_ext[0]['description']
        print("extracted text: ", extracted_text)

        for each_ext_extracted in text_ext:
            if "micro" == each_ext_extracted["description"].lower():
                bounding_box = each_ext_extracted["boundingPoly"]["vertices"]
                break

    except Exception as e:
        print("Error in parsing text from image: {}".format(e))

    return bounding_box


def get_crop_img(image_url, bounding_box):
    if bounding_box is None or bounding_box == []:
        return False
    img_pil_obj = get_image_pil_object_from_image_path(image_url)
    x_coordinates = [point['x'] for point in bounding_box]
    y_coordinates = [point['y'] for point in bounding_box]
    left = min(x_coordinates)
    top = min(y_coordinates)
    right = max(x_coordinates)
    bottom = max(y_coordinates)
    offset = 0.08*bottom
    #offset = 40   # TODO: Percent of image dimension
    bottom += offset
    bottom = min(bottom, img_pil_obj.height)

    cropped_image = img_pil_obj.crop((left, top, right, bottom))
    cropped_image.save('cropped_img.png')
    return True


def apply_sift_matching(image_path, template_path):
    search_image = cv2.imread(image_path, cv2.COLOR_BGR2GRAY)
    logo_image = cv2.imread(template_path, cv2.COLOR_BGR2GRAY)
    #search_image = normalize(search_image)
    #logo_image = normalize(logo_image)
    sift = cv2.SIFT_create()
    kp_product, des_product = sift.detectAndCompute(search_image, None)
    kp_template, des_template = sift.detectAndCompute(logo_image, None)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des_template, des_product, k=2)
    knn_threshold = 0.75

    matchesMask = [[0, 0] for i in range(len(matches))]
    for i, (m, n) in enumerate(matches):
        if m.distance < knn_threshold * n.distance:
            matchesMask[i] = [1, 0]
    draw_params = dict(matchColor=(0, 255, 0), singlePointColor=(255, 0, 0), matchesMask=matchesMask, flags=0)
    img3 = cv2.drawMatchesKnn(logo_image, kp_template, search_image, kp_product, matches, None, **draw_params)
    plt.imshow(img3)
    plt.savefig("test_img_box_sift.png")

    good_matches = []
    for m, n in matches:
        if m.distance < knn_threshold * n.distance:
            good_matches.append(m)
    print("no of matches found: {}".format(len(good_matches)))

    min_good_matches = 6
    if len(good_matches) >= min_good_matches:
        return True
    else:
        return False

# Load the pretrained model
model = models.resnet18(pretrained=True)
# Use the model object to select the desired layer
layer = model._modules.get('avgpool')
# Set model to evaluation mode
model.eval()

# Image transforms
scaler = transforms.Resize((224, 224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
to_tensor = transforms.ToTensor()

def get_resnet_vector(image_name):
    # 1. Load the image with Pillow library
    img = Image.open(image_name).convert("RGB")
    """
    # Image preprocessing
    img = np.array(img)
    img = cv2.equalizeHist(img)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = Image.fromarray(img)
    """

    # 2. Create a PyTorch Variable with the transformed image
    t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
    # 3. Create a vector of zeros that will hold our feature vector
    #    The 'avgpool' layer has an output size of 512
    #     my_embedding = torch.zeros(512)
    my_embedding = torch.zeros(1, 512, 1, 1)

    # 4. Define a function that will copy the output of a layer
    def copy_data(m, i, o):
        my_embedding.copy_(o.data)

    # 5. Attach that function to our selected layer
    h = layer.register_forward_hook(copy_data)
    # 6. Run the model on our transformed image
    model(t_img)
    # 7. Detach our copy function from the layer
    h.remove()
    # 8. Return the feature vector
    l1 = []
    for itr in my_embedding[0]:
        l1.append(float(itr[0][0]))
    return l1


if __name__ == "__main__":
    image_url = "/home/akshay/Desktop/DW/Product_matching/newegg/test_image_13.jpg"
    template_url = "/home/akshay/Desktop/DW/Product_matching/newegg/query_logo_refit.png"
    cropped_img_url = "/home/akshay/Desktop/dev/pyProject/logo_detection/cropped_img.png"

    #image_url = "/home/akshay/Desktop/DW/Product_matching/newegg/test_img_isi5.png"
    #template_url = "/home/akshay/Desktop/DW/Product_matching/newegg/benchmark_isi_logo.png"

    bounding_box = get_text_from_image(image_url, "image")
    print("bounding box: {}".format(bounding_box))
    crop_done = get_crop_img(image_url, bounding_box)
    if crop_done is False:
        print("cropping not done")
        cropped_img_url = image_url

    print(apply_sift_matching(cropped_img_url, template_url))
    v1 = get_resnet_vector(template_url)
    v2 = get_resnet_vector(cropped_img_url)
    cos_sim = dot(v1, v2) / (norm(v1) * norm(v2)) * 100
    print(cos_sim)





