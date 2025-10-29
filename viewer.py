import napari
import cv2
import numpy as np
import json
import os
from handlers.MultiInstanceLabel import MultiInstanceLabel
from handlers.ImageHandler import ImageHandler
from widgets.multilabeler import MultiLabelerWidget
from widgets.imageselector import ImageSelectorWidget

class MainApp:
    def __init__(self, viewer, dataset_path):
        self.viewer = viewer
        self.dataset = self.prepare_dataset(dataset_path)
        self.mil = MultiInstanceLabel(self.dataset[0][0], self.dataset[0][1])
        self.imhandler = ImageHandler(viewer, self.dataset, self.mil)

        self.multilabeler = MultiLabelerWidget(viewer, self.mil)
        self.imselector = ImageSelectorWidget(viewer, self.imhandler)
        viewer.window.add_dock_widget(self.imselector, area='left')
        viewer.window.add_dock_widget(self.multilabeler, area='left')

        napari.run()


    def prepare_dataset(self, dataset_path):
        dataset = []
        for subdir, _, files in os.walk(dataset_path):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(subdir, file)
                    img_path = json_path.replace('.json', '.png')
                    dataset.append((img_path, json_path))
        return dataset

dataset_path = "/Users/lucajaich/Documents/chronoroot/Datasets/LongPlantsSeg/train/Etiolation/rpi102_2024-06-11_14-10/3 listo"
MainApp(napari.Viewer(), dataset_path)