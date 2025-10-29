from handlers.MultiInstanceLabel import MultiInstanceLabel

class ImageHandler:
    def __init__(self, viewer, dataset, global_mil, on_new_mil):
        self.viewer = viewer
        self.dataset = dataset
        self.current_index = 0
        self.mil = global_mil
        self.on_new_mil = on_new_mil

        self.load_image_and_annotations()

    def load_image_and_annotations(self):
        img_path, ann_path = self.dataset[self.current_index]
        new_mil = MultiInstanceLabel(img_path, ann_path)
        self.on_new_mil(new_mil)
        self.mil = new_mil
        labels = self.mil.get_labels_for_display()

        # clear existing layers (safe)
        self.viewer.layers.clear()

        # add image using the existing viewer instead of creating a new one
        image_layer = self.viewer.add_image(self.mil.img, name='image')

        # create a 'label' layer here
        label_layer = self.viewer.add_labels(labels, name='labels')

        bboxes, features, text_params = self.mil.get_bboxes_for_display()

        # create the features table
        shapes_layer = self.viewer.add_shapes(
            bboxes,
            face_color='transparent',
            edge_color='green',
            edge_width=3,
            name='bboxes',
            features=features,
            text=text_params,
        )


    def next_image(self):
        if self.current_index < len(self.dataset) - 1:
            self.current_index += 1
            self.load_image_and_annotations()

    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image_and_annotations()