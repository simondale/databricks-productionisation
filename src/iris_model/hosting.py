from flask import Flask, Response, request
from flask_restful import Resource, Api

import mlflow
import mlflow.sklearn
import pandas as pd

app = Flask(__name__)
api = Api(app)


mlflow.set_tracking_uri('databricks')
model = mlflow.sklearn.load_model('models:/iris/None')


@app.route('/predict', methods=['POST'])
def predict():
    body = request.get_data()
    pdf = pd.read_json(body, orient='split')
    pdf['prediction'] = model.predict(pdf)
    return Response(pdf.to_json(orient='split'), status=200)


def run(host: str, port: int):
    app.run(host=host, port=port)
