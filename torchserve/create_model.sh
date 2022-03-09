torch-model-archiver --model-name scalenet --version 1.0 --model-file scalenet/model_RCNN_only.py --handler scalenet/handler.py --export-path model_store -f --extra-files "scalenet/helper.py,scalenet/parameter_estimination.pt"

cd yolov5_torchserve

torch-model-archiver --model-name yolov5 -f \
--version 0.1 --serialized-file ressources/yolov5s.pt \
--handler ressources/torchserve_handler.py \
--extra-files ressources/yolov5/,ressources/torchserve_handler.py,ressources/mask.pt \
--export-path ../model_store