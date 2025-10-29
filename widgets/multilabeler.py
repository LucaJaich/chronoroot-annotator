import napari
import numpy as np
from qtpy.QtWidgets import (
    QPushButton, 
    QWidget, 
    QHBoxLayout, 
    QLabel, 
    QSpinBox,
    QVBoxLayout
)
from handlers.MultiInstanceLabel import MultiInstanceLabel


class IdleWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer", mil: "MultiInstanceLabel", switch_to_labeling):
        super().__init__()
        self.viewer = viewer
        self.mil = mil
        self.switch_to_labeling = switch_to_labeling

        self.build_layout()


    def build_layout(self):
        self.setLayout(QVBoxLayout())

        row1 = QHBoxLayout()
        self.label_instance = QLabel("Select an instance:")
        self.instance_id = QSpinBox()
        self.instance_id.setMinimum(0)
        self.instance_id.setMaximum(self.mil.n_labels - 1)
        self.instance_id.setValue(1)
        row1.addWidget(self.label_instance)
        row1.addWidget(self.instance_id)
        self.layout().addLayout(row1)

        row2 = QHBoxLayout()
        self.label_new = QLabel("Select how many new instances:")
        self.new_instances = QSpinBox()
        self.new_instances.setMinimum(0)
        self.new_instances.setMaximum(self.mil.n_labels - 1)
        self.new_instances.setValue(1)
        row2.addWidget(self.label_new)
        row2.addWidget(self.new_instances)
        self.layout().addLayout(row2)

        row3 = QHBoxLayout()
        self.btn = QPushButton("Anotar!")
        self.btn.clicked.connect(self.on_click)
        row3.addWidget(self.btn)
        self.layout().addLayout(row3)


    def on_click(self):
        self.switch_to_labeling(self.instance_id.value(), self.new_instances.value())


class LabelingWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer", mil: "MultiInstanceLabel", instance_id, new_instances, switch_to_idle):
        super().__init__()
        self.viewer = viewer
        self.mil = mil
        self.n_new_instances = new_instances
        self.switch_to_idle = switch_to_idle
        self.instance_id = instance_id
        self.current_new_instance_id = 0
        self.new_instances_mask = np.stack([self.mil.instance_masks[self.instance_id]] * self.n_new_instances)
        self.current_instance_layer = None
        print(f"New instance mask shape: {self.new_instances_mask.shape}")           

        self.build_layout()
        self._check_buttons_ability()


    def build_layout(self):
        self.setLayout(QVBoxLayout())

        row1 = QHBoxLayout()
        self.btn_next = QPushButton("Siguiente")
        self.btn_next.clicked.connect(self.on_click_next)
        self.btn_previous = QPushButton("Anterior")
        self.btn_previous.clicked.connect(self.on_click_previous)
        row1.addWidget(self.btn_previous)
        row1.addWidget(self.btn_next)
        self.layout().addLayout(row1)

        row2 = QHBoxLayout()
        self.btn_finish = QPushButton("Terminar")
        self.btn_finish.clicked.connect(self.on_click_finish)
        row2.addWidget(self.btn_finish)
        self.layout().addLayout(row2)

        # Hide label and bbox layers if present
        if "labels" in self.viewer.layers:
            self.viewer.layers["labels"].visible = False
        if "bboxes" in self.viewer.layers:
            self.viewer.layers["bboxes"].visible = False

        self.new_instance_mask = self.mil.instance_masks[self.instance_id]
        self.current_instance_layer = self.viewer.add_labels(self.new_instance_mask, name='temp_label_0')


    def on_click_next(self):
        self._update_mask()
        self.current_new_instance_id += 1
        self._update_viewer()


    def on_click_previous(self):
        self._update_mask()
        self.current_new_instance_id -= 1
        self._update_viewer()


    def on_click_finish(self):
        self._remove_temp_label()

        self.mil.update_instance(self.instance_id, self.new_instances_mask)
        new_labels = self.mil.get_labels_for_display()
        self.viewer.layers["labels"].data = new_labels
        bboxes, features, text_params = self.mil.get_bboxes_for_display()
        self.viewer.layers["bboxes"].data = bboxes
        self.viewer.layers["bboxes"].features = features
        self.viewer.layers["bboxes"].text = text_params

        self.switch_to_idle()


    def _check_buttons_ability(self):
        if self.current_new_instance_id == 0:
            self.btn_previous.setEnabled(False)
            self.btn_next.setEnabled(True)
        elif self.current_new_instance_id == self.n_new_instances - 1:
            self.btn_previous.setEnabled(True)
            self.btn_next.setEnabled(False)
        else:
            self.btn_previous.setEnabled(True)
            self.btn_next.setEnabled(True)


    def _update_viewer(self):
        self._check_buttons_ability()
        self._remove_temp_label()
        self.current_instance_layer = self.viewer.add_labels(self.new_instances_mask[self.current_new_instance_id], name=f'temp_label_{self.current_new_instance_id}')


    def _remove_temp_label(self):
        for layer in self.viewer.layers:
            if layer.name.startswith('temp_label_'):
                self.viewer.layers.remove(layer)
                break


    def _update_mask(self):
        self.new_instances_mask[self.current_new_instance_id] = self.current_instance_layer.data


class MultiLabelerWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer", mil: "MultiInstanceLabel"):
        super().__init__()
        self.viewer = viewer
        self.mil = mil

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.idle_widget = IdleWidget(viewer, mil, self.switch_to_labeling)
        self.layout.addWidget(self.idle_widget)


    def switch_to_labeling(self, instance_id, new_instances):
        self.layout.removeWidget(self.idle_widget)
        self.idle_widget.setParent(None)
        self.labeling_widget = LabelingWidget(self.viewer, self.mil, instance_id, new_instances, self.switch_to_idle)
        self.layout.addWidget(self.labeling_widget)


    def switch_to_idle(self):
        # detach labeling widget
        self.layout.removeWidget(self.labeling_widget)
        self.labeling_widget.setParent(None)

        # make previous layers visible again
        if "labels" in self.viewer.layers:
            self.viewer.layers["labels"].visible = True
        if "bboxes" in self.viewer.layers:
            self.viewer.layers["bboxes"].visible = True

        # attach idle widget
        self.idle_widget = IdleWidget(self.viewer, self.mil, self.switch_to_labeling)
        self.layout.addWidget(self.idle_widget)
