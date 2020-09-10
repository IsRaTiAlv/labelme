from PIL import Image
import torchvision
import torchvision.transforms as T
import mask2poly
from skimage import measure
import numpy as np

class autolabeling:
    def __init__(self):
        self.model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
        self.model.eval()
        self.class_names = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

    def get_prediction(self, img_path, threshold):
        img = Image.open(img_path)
        transform = T.Compose([T.ToTensor()])
        img = transform(img)
        pred = self.model([img])
        pred_score = list(pred[0]['scores'].detach().numpy())
        pred_t = [pred_score.index(x) for x in pred_score if x>threshold][-1]
        masks = (pred[0]['masks']>0.5).squeeze().detach().cpu().numpy()
        pred_class = [self.class_names[i] for i in list(pred[0]['labels'].numpy())]
        pred_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(pred[0]['boxes'].detach().numpy())]
        if(len(masks.shape)==3):
            masks = masks[:pred_t+1]
        else:
            masks = np.expand_dims(masks,0)
        pred_boxes = pred_boxes[:pred_t+1]
        pred_class = pred_class[:pred_t+1]
        return masks, pred_boxes, pred_class

    def inference(self, img_path, poly_rate = 10):
        # im = cv2.imread("/home/israel/repos/labelme/examples/test/gait1.jpg")
        masks, _, labels = self.get_prediction(img_path,0.5)
        # masks = outputs['instances'].pred_masks.to('cpu').numpy()
        # labels = outputs['instances'].pred_classes.to('cpu').numpy()
        shapes = []
        for i, label in enumerate(labels):
            # _, _, polygons = binary_mask_to_polygon(masks[i], 0)
            contour = measure.find_contours(masks[i],0)[0]
            polygons = np.flip(contour, axis=1)

            points = polygons[::poly_rate]
            points = list(map(tuple, points.astype('float')))
            instance = {'label': label,
                        'points': points,
                        'group_id': None,
                        'shape_type': 'polygon',
                        'flags': {}}
            shapes.append(instance)
        return shapes

    def bbox_inference(self, img_path):
        # im = cv2.imread("/home/israel/repos/labelme/examples/test/gait1.jpg")
        _, pred_boxes, labels = self.get_prediction(img_path,0.5)
        # masks = outputs['instances'].pred_masks.to('cpu').numpy()
        # labels = outputs['instances'].pred_classes.to('cpu').numpy()
        shapes = []
        for i, label in enumerate(labels):
            # _, _, polygons = binary_mask_to_polygon(masks[i], 0)
            instance = {'label': label,
                        'points': list(([list(map(float,pred_boxes[i][0])), list(map(float,pred_boxes[i][1]))])),
                        'group_id': None,
                        'shape_type': 'rectangle',
                        'flags': {}}
            shapes.append(instance)
        return shapes

    def class_inference(self, img_path):
        # im = cv2.imread("/home/israel/repos/labelme/examples/test/gait1.jpg")
        _, _, labels = self.get_prediction(img_path,0.5)
        # masks = outputs['instances'].pred_masks.to('cpu').numpy()
        # labels = outputs['instances'].pred_classes.to('cpu').numpy()
        flags = {}
        for i, name in enumerate(self.class_names):
            flags.update({name:True if labels[0]==name else False})
        return flags
