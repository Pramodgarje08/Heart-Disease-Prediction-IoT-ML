from pathlib import Path
import requests, zipfile
root=Path(__file__).resolve().parents[1]; data=root/'data'; data.mkdir(exist_ok=True)
u='https://www.kaggle.com/api/v1/datasets/download/jocelyndumlao/cardiovascular-disease-dataset'
out=data/'indian_cvd.zip'
r=requests.get(u,timeout=90); r.raise_for_status(); out.write_bytes(r.content)
with zipfile.ZipFile(out) as z: z.extractall(data)
print('Downloaded Indian CVD dataset to',data)
