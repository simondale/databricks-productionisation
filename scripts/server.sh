#! /bin/bash
eval "$(~/miniconda3/bin/conda shell.bash hook)"
conda activate hosting
gunicorn --bind "0.0.0.0:5000" iris_model.hosting:app