from pycocotools.mask import decode as decodeMask
from pycocotools.mask import encode as encodeMask
import numpy as np
import json
import cv2

class MultiInstanceLabel:
    def __init__(self, img_path, ann_path):
        self.img_path = img_path
        self.img = cv2.imread(img_path)
        self.ann_path = ann_path
        self.ann = json.load(open(ann_path))
        self.instance_masks = [decodeMask(a['segmentation']) for a in self.ann['annotations']]
        self.n_labels = len(self.instance_masks)
        self.bboxes = [a['bbox'] for a in self.ann['annotations']]


    def get_labels_for_display(self):
        """
        Returns:
            np.ndarray: A 2D array where each pixel's value corresponds to the instance label
        """
        labels = np.zeros(self.img.shape[:2], dtype=np.uint8)
        for i, mask in enumerate(self.instance_masks):
            labels[mask.astype(bool)] = i 
        return labels
    
    def save_ann(self):
        with open(self.ann_path, "w") as f:
            json.dump(self.ann, f, indent=4)  

    def get_bboxes_for_display(self):
        """
        The bounding boxes are in the format [ymin, xmin, ymax, xmax]
        Returns:
            np.ndarray: An array of shape (n, 4, 2) where n is the number of bounding boxes,
                        and each bounding box is represented by its four corner points.
        """
        rects = [[
            [a['bbox'][1], a['bbox'][0]],
            [a['bbox'][1], a['bbox'][2]],
            [a['bbox'][3], a['bbox'][2]],
            [a['bbox'][3], a['bbox'][0]]
        ] for a in self.ann['annotations']]

        features = {
            'instance': [str(i) for i in range(self.n_labels)],
        }

        # specify the display parameters for the text
        text_params = {
            'string': 'instance: {instance}',
            'size': 8,
            'color': 'green',
            'anchor': 'upper_left',
            'translation': [-3, 0]
        }

        return np.array(rects), features, text_params
    
    def update_instance(self, instance_id, new_instance_masks):
        """
        Update the instance masks for a specific instance ID.

        Args:
            instance_id (int): The ID of the instance to update.
            new_instance_masks (np.ndarray): A 3D array where each slice along the first axis
                                             is a binary mask for a new instance.
        """
        if instance_id < 0 or instance_id >= self.n_labels:
            raise ValueError("Invalid instance ID")
        
        # Remove the old instance mask
        del self.instance_masks[instance_id]
        del self.ann['annotations'][instance_id]
        print("START:",len(self.ann["annotations"]))
        # Add the new instance masks
        for new_mask in new_instance_masks:
            self.instance_masks.append(new_mask)
            # Create a new annotation entry (you might want to customize this)
            rle = encodeMask(np.asarray(new_mask, order="F"))
            rle["counts"] = rle["counts"].decode("utf-8")
            bbox = self._mask_to_bbox(new_mask)
            new_ann = {
                "bbox_mode": 0,
                'segmentation': rle,
                'bbox': bbox,
                'category_id': 1,  # Assuming a single category; adjust as needed
            }
            self.ann['annotations'].append(new_ann)
            print(bbox)

        print("END:", len(self.ann["annotations"]))
        self.n_labels = len(self.instance_masks) 
        self.save_ann()
    
    def _mask_to_bbox(self, mask):
        """
        Convert a binary mask to a bounding box in the format [min_y, min_x, max_y, max_x].

        Args:
            mask (np.ndarray): A binary mask.
        Returns:
            list: A list representing the bounding box [min_y, min_x, max_y, max_x].
        """

        ys, xs = np.where(mask)
        if len(xs) == 0 or len(ys) == 0:
            return [0, 0, 0, 0]  # No object found
        min_x, max_x = xs.min(), xs.max()
        min_y, max_y = ys.min(), ys.max()
        return [int(min_x), int(min_y), int(max_x), int(max_y)]
    
