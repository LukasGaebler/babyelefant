from ts.torch_handler.base_handler import BaseHandler
from ts.utils.util import PredictionException
import numpy as np
import cv2

from model_RCNN_only import RCNN_only

class ModelHandler(BaseHandler):
    """
    A custom model handler implementation.
    """
    
    def __init__(self):
        super().__init__()
        self._context = None
        self.initialized = False
        self.device = None
        self.model = RCNN_only()
        
        
    def initialize(self, context):
        self._context = context
        self.initialized = True
        
    def preprocess(self, data):
        out = []
        for id,byte_array in data[0].items():
            file_bytes = np.asarray(bytearray(byte_array), dtype=np.uint8)
            out.append(cv2.imdecode(file_bytes, cv2.IMREAD_COLOR))
        
        return out
         

    def inference(self, model_input):
        output = []
        for img in model_input:
            output.append(self.model(img))
        return output
    
    def postprocess(self, data):
        out = []
        
        for pred in data:
            out.append(dict(pred._asdict()))
        
        return [out]