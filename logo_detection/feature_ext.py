
import numpy as np
import cv2
import matplotlib.pyplot as plt

def match_template(image_path, template_path):
    template = cv2.imread(template_path, 0)
    product_image = cv2.imread(image_path, 0)

    (h, w) = template.shape[:2]

    res = cv2.matchTemplate(product_image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(product_image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    cv2.imshow('Detected Logos', product_image)
    while True:
        k = cv2.waitKey(0)
        if k == 27:  # ESC key
            cv2.destroyAllWindows()
            break
"""
def match_template(image_path, template_path):
    template = cv2.imread(template_path, 0)
    product_image = cv2.imread(image_path, 0)

    (h, w) = template.shape[:2]

    res = cv2.matchTemplate(product_image, template, cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(product_image, top_left, bottom_right, 175, 2)
    plt.subplot(121), plt.imshow(res, cmap='gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(product_image, cmap='gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.savefig("test_matchtemplate.png")
"""


def detect_logo(image_path, template_path):
    product_image = cv2.imread(image_path)
    logo_template = cv2.imread(template_path)

    sift = cv2.SIFT_create()

    kp_product, des_product = sift.detectAndCompute(product_image, None)
    kp_template, des_template = sift.detectAndCompute(logo_template, None)

    bf = cv2.BFMatcher()

    matches = bf.knnMatch(des_template, des_product, k=2)
    knn_threshold = 0.5

    matchesMask = [[0, 0] for i in range(len(matches))]
    for i, (m, n) in enumerate(matches):
        if m.distance < knn_threshold * n.distance:
            matchesMask[i] = [1, 0]
    draw_params = dict(matchColor=(0, 255, 0), singlePointColor=(255, 0, 0), matchesMask=matchesMask, flags=0)
    img3 = cv2.drawMatchesKnn(logo_template, kp_template, product_image, kp_product, matches, None, **draw_params)
    plt.imshow(img3)
    plt.savefig("test_img_feature_ext.png")

    good_matches = []
    for m, n in matches:
        if m.distance < knn_threshold * n.distance:
            good_matches.append(m)

    min_good_matches = 10
    if len(good_matches) >= min_good_matches:
        return True
    else:
        return False


if __name__ == "__main__":
    product_image_path = "/home/akshay/Desktop/dev/pyProject/logo_detection/cropped_img.png"
    logo_template_path = "/home/akshay/Desktop/DW/Product_matching/newegg/benchmark_isi_logo.png"

    logo_present = detect_logo(product_image_path, logo_template_path)
    if logo_present:
        print("Logo is present in the product image.")
    else:
        print("Logo is not present in the product image.")

    match_template(product_image_path, logo_template_path)

