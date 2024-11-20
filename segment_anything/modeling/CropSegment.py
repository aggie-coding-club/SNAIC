import torch
import numpy as np
import cv2
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamPredictor
from segment_anything.utils.onnx import SamOnnxModel
import warnings
import requests
import os

import onnxruntime
from onnxruntime.quantization import QuantType
from onnxruntime.quantization.quantize import quantize_dynamic



def show_mask(mask, ax):
    color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    
def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)   
    
def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2)) 




checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

try:
    sam = sam_model_registry[model_type](checkpoint=checkpoint)
except:
    url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    r = requests.get(url, allow_redirects=True)
    open("sam_vit_h_4b8939.pth","wb").write(r.content)
    sam = sam_model_registry[model_type](checkpoint=checkpoint)

onnx_model_path = "sam_onnx_example.onnx"

onnx_model = SamOnnxModel(sam, return_single_mask=True)

dynamic_axes = {
    "point_coords": {1: "num_points"},
    "point_labels": {1: "num_points"},
}

embed_dim = sam.prompt_encoder.embed_dim
embed_size = sam.prompt_encoder.image_embedding_size
mask_input_size = [4 * x for x in embed_size]
dummy_inputs = {
    "image_embeddings": torch.randn(1, embed_dim, *embed_size, dtype=torch.float),
    "point_coords": torch.randint(low=0, high=1024, size=(1, 5, 2), dtype=torch.float),
    "point_labels": torch.randint(low=0, high=4, size=(1, 5), dtype=torch.float),
    "mask_input": torch.randn(1, 1, *mask_input_size, dtype=torch.float),
    "has_mask_input": torch.tensor([1], dtype=torch.float),
    "orig_im_size": torch.tensor([1500, 2250], dtype=torch.float),
}
output_names = ["masks", "iou_predictions", "low_res_masks"]

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=torch.jit.TracerWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    with open(onnx_model_path, "wb") as f:
        torch.onnx.export(
            onnx_model,
            tuple(dummy_inputs.values()),
            f,
            export_params=True,
            verbose=False,
            opset_version=17,
            do_constant_folding=True,
            input_names=list(dummy_inputs.keys()),
            output_names=output_names,
            dynamic_axes=dynamic_axes,
        )    


# INPUT AREA
#
# Upload image to folder, and change name below.
# Also make sure to update np.array values to make sense with your image.
def generateMask(imageName,x,y):
    rawImage = cv2.imread(imageName)
    image = cv2.resize(rawImage, (1800, 1200))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    ort_session = onnxruntime.InferenceSession(onnx_model_path)

    sam.to(device='cuda')
    predictor = SamPredictor(sam)
    predictor.set_image(image)
    image_embedding = predictor.get_image_embedding().cpu().numpy()
    image_embedding.shape
    # Uses one point value -- edit this for each image.
    input_point = np.array([[x, y]])
    input_label = np.array([1])

    onnx_coord = np.concatenate([input_point, np.array([[0.0, 0.0]])], axis=0)[None, :, :]
    onnx_label = np.concatenate([input_label, np.array([-1])], axis=0)[None, :].astype(np.float32)

    onnx_coord = predictor.transform.apply_coords(onnx_coord, image.shape[:2]).astype(np.float32)

    onnx_mask_input = np.zeros((1, 1, 256, 256), dtype=np.float32)
    onnx_has_mask_input = np.zeros(1, dtype=np.float32)

    ort_inputs = {
        "image_embeddings": image_embedding,
        "point_coords": onnx_coord,
        "point_labels": onnx_label,
        "mask_input": onnx_mask_input,
        "has_mask_input": onnx_has_mask_input,
        "orig_im_size": np.array(image.shape[:2], dtype=np.float32)
    }

    masks, _, low_res_logits = ort_session.run(None, ort_inputs)
    masks = masks > predictor.model.mask_threshold
    
    mask = masks[0, 0].astype(np.uint8)  # Extract the first mask and convert to uint8
    mask = mask * 255  # Scale to 0-255 for OpenCV compatibility

    # Apply the mask to isolate the segmented part of the image
    segmented_image = cv2.bitwise_and(image, image, mask=mask)

    # Crop the region of interest
    x, y, w, h = cv2.boundingRect(mask)
    cropped_segment = segmented_image[y:y+h, x:x+w]

    # Save the results
    cv2.imwrite("segmented_output.png", cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR))
    cv2.imwrite("cropped_segment.png", cv2.cvtColor(cropped_segment, cv2.COLOR_RGB2BGR))

    # Display the results
    plt.figure(figsize=(10, 10))
    plt.subplot(1, 2, 1)
    plt.title("Segmented Image")
    plt.imshow(segmented_image)
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Cropped Segment")
    plt.imshow(cropped_segment)
    plt.axis('off')

    plt.show()

    return


# plt.figure(figsize=(10,10))
# plt.imshow(image)
# show_mask(masks, plt.gca())
# show_points(input_point, input_label, plt.gca())
# plt.axis('off')
# plt.show() 




# # Uses two points -- edit this for each image.
# input_point = np.array([[375, 300], [1500, 350]])
# input_label = np.array([1, 1])

# # Use the mask output from the previous run. It is already in the correct form for input to the ONNX model.
# onnx_mask_input = low_res_logits

# onnx_coord = np.concatenate([input_point, np.array([[0.0, 0.0]])], axis=0)[None, :, :]
# onnx_label = np.concatenate([input_label, np.array([-1])], axis=0)[None, :].astype(np.float32)

# onnx_coord = predictor.transform.apply_coords(onnx_coord, image.shape[:2]).astype(np.float32)
# onnx_has_mask_input = np.ones(1, dtype=np.float32)
# ort_inputs = {
#     "image_embeddings": image_embedding,
#     "point_coords": onnx_coord,
#     "point_labels": onnx_label,
#     "mask_input": onnx_mask_input,
#     "has_mask_input": onnx_has_mask_input,
#     "orig_im_size": np.array(image.shape[:2], dtype=np.float32)
# }

# masks, _, _ = ort_session.run(None, ort_inputs)
# masks = masks > predictor.model.mask_threshold
# plt.figure(figsize=(10,10))
# plt.imshow(image)
# show_mask(masks, plt.gca())
# show_points(input_point, input_label, plt.gca())
# plt.axis('off')
# plt.show() 
# mask_image = (masks * 255).astype(np.uint8)
# cv2.imwrite('mask2.png', mask_image)


# # Creates a box, and uses a point in the box -- edit this for each image.
# #                        (x1,y1,x2,y2)
# input_box = np.array([425, 600, 700, 875])
# input_point = np.array([[575, 750]])
# input_label = np.array([0])
# onnx_box_coords = input_box.reshape(2, 2)
# onnx_box_labels = np.array([2,3])

# onnx_coord = np.concatenate([input_point, onnx_box_coords], axis=0)[None, :, :]
# onnx_label = np.concatenate([input_label, onnx_box_labels], axis=0)[None, :].astype(np.float32)

# onnx_coord = predictor.transform.apply_coords(onnx_coord, image.shape[:2]).astype(np.float32)

# onnx_mask_input = np.zeros((1, 1, 256, 256), dtype=np.float32)
# onnx_has_mask_input = np.zeros(1, dtype=np.float32)

# ort_inputs = {
#     "image_embeddings": image_embedding,
#     "point_coords": onnx_coord,
#     "point_labels": onnx_label,
#     "mask_input": onnx_mask_input,
#     "has_mask_input": onnx_has_mask_input,
#     "orig_im_size": np.array(image.shape[:2], dtype=np.float32)
# }

# masks, _, _ = ort_session.run(None, ort_inputs)
# masks = masks > predictor.model.mask_threshold
# plt.figure(figsize=(10, 10))
# plt.imshow(image)
# show_mask(masks[0], plt.gca())
# show_box(input_box, plt.gca())
# show_points(input_point, input_label, plt.gca())
# plt.axis('off')
# plt.show()