import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

import numpy as np
import cv2
import random
from imantics import Polygons, Mask


class predict:
    def __init__(self):
        cfg = get_cfg()
        cfg.merge_from_file("/home/israel/repos/detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 # set threshold for this model
        cfg.MODEL.WEIGHTS = "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl"
        cfg.MODEL.DEVICE='cpu'
        self.predictor = DefaultPredictor(cfg)
        self.class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes

    def inference(self, img_path):
        # im = cv2.imread("/home/israel/repos/labelme/examples/test/gait1.jpg")
        im = cv2.imread(img_path)
        outputs = self.predictor(im)
        masks = outputs['instances'].pred_masks.to('cpu').numpy()
        labels = outputs['instances'].pred_classes.to('cpu').numpy()
        shapes = []
        for i, label in enumerate(labels):
            polygons = Mask(masks[i]).polygons()
            points = polygons.points[0][::5]
            points = list(map(tuple, points.astype('float')))
            instance = {'label': self.class_names[label],
                        'points': points,
                        'group_id': None,
                        'shape_type': 'polygon',
                        'flags': {}}
            shapes.append(instance)
        return shapes
