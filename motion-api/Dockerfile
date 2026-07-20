FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

RUN apt-get update && apt-get install -y \
    git ffmpeg unzip build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    numpy==1.23.5 scipy scikit-learn matplotlib pillow h5py tqdm \
    spacy==3.7.5 gdown chumpy smplx==0.1.28 \
    ftfy regex moviepy imageio imageio-ffmpeg trimesh joblib \
    fastapi uvicorn[standard]

RUN python -m spacy download en_core_web_sm
RUN pip install --no-cache-dir git+https://github.com/openai/CLIP.git

# chumpyが古いPython API(inspect.getargspec、Python3.11で削除済み)を使っているためパッチを当てる
RUN find / -path "*/chumpy/ch.py" -exec sed -i 's/inspect.getargspec/inspect.getfullargspec/g' {} \;

WORKDIR /app
COPY app.py export_vrm_pose.py ./

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]
