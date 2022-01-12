import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import os
from torch.optim.lr_scheduler import MultiStepLR, ReduceLROnPlateau
from tensorboardX import SummaryWriter
from tqdm import tqdm
from ai.scalenet_calibration.model_RCNN_only import RCNN_only
from ai.scalenet_calibration.utils.compute_vectors import generate_field
from ai.scalenet_calibration.utils.config import cfg
import ai.scalenet_calibration.utils.model_utils as model_utils
from ai.scalenet_calibration.utils.logger import setup_logger, printer
from ai.scalenet_calibration.utils.train_utils import *
#from ai.scalenet_calibration.utils.checkpointer import DetectronCheckpointer
from ai.scalenet_calibration.utils.utils_misc import *
import inspect
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from PIL import Image
from ai.scalenet_calibration.dataset_cvpr import bins2roll, bins2vfov, bins2horizon, bins2pitch
from ai.scalenet_calibration.utils.matrix import get_overhead_hmatrix_from_4cameraparams, get_scaled_homography
import cv2
import argparse
#import maskrcnn_benchmark
#from maskrcnn_benchmark.utils.comm import synchronize, get_rank

import sys
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.insert(0, current_dir)

torch.set_grad_enabled(False)


parser = argparse.ArgumentParser(
    description="Rui's Scale Estimation Network Training")

# Model
parser.add_argument(
    '--accu_model',
    action='store_true',
    help='Use accurate model with theta instead of Derek\'s approx.')
# Pretraining
parser.add_argument(
    '--resume',
    type=str,
    help='resume training; can be full path (e.g. tmp/checkpoint0.pth.tar) or taskname (e.g. tmp)',
    default='NoCkpt')
parser.add_argument(
    '--feature_only',
    action='store_true',
    help='restore only features (remove all classifiers) from checkpoint')
# Device
parser.add_argument('--cpu', action='store_true', help='Force training on CPU')
parser.add_argument("--local_rank", type=int, default=0)
parser.add_argument("--master_port", type=str, default='8914')
# DEBUG
parser.add_argument('--debug', action='store_true', help='Debug eval')
# Mask R-CNN
parser.add_argument('--not_rcnn', action='store_true',
                    help='Disable Mask R-CNN module')

parser.add_argument('--pointnet_camH', action='store_true', help='')
parser.add_argument('--est_bbox', action='store_true',
                    help='Enable estimating bboxes instead of using GT bboxes')

parser.add_argument(
    "--config-file",
    default="",
    metavar="FILE",
    help="path to config file",
    type=str,
)
parser.add_argument(
    "opts",
    help="Modify config options using the command-line",
    default=None,
    nargs=argparse.REMAINDER,
)

# opt = parser.parse_args()
opt = parser.parse_args(
    '--accu_model --resume YES \
--config-file ai/scalenet_calibration/coco_config_small_RCNNOnly.yaml \
SOLVER.IMS_PER_BATCH 1 TEST.IMS_PER_BATCH 1'.split())

opt.checkpoints_folder = 'checkpoint'

device = 'cpu'

# config_file = "maskrcnn/coco_config.yaml"
config_file = opt.config_file
cfg.merge_from_file(config_file)
# manual override some options
cfg.merge_from_list(["MODEL.DEVICE", device])
cfg.merge_from_list(opt.opts)
cfg.freeze()
opt.cfg = cfg


model = RCNN_only(cfg, opt, printer, rank=True)
model.to(device)

model.eval()

def calibration(cv2_image):  
    output_RCNN = model(cv2_image)
    output_RCNN.output_horizon
    pitch = output_RCNN.output_pitch
    roll = output_RCNN.output_roll
    vfov = output_RCNN.output_vfov

    w, h,c = cv2_image.shape
    f_pix = h / 2. / np.tan(vfov / 2.)

    print(pitch,roll,vfov)

    sensor_size = 24 
    f_pix / h * sensor_size

    overhead_hmatrix, est_range_u, est_range_v = get_overhead_hmatrix_from_4cameraparams(
        fx=f_pix, fy=f_pix, my_tilt=pitch, my_roll=-roll, img_dims=(w, h), verbose=False)

    scaled_overhead_hmatrix, target_dim = get_scaled_homography(
        overhead_hmatrix, 1080 * 2, est_range_u, est_range_v)

    return scaled_overhead_hmatrix
