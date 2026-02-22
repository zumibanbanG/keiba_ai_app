from google.cloud import storage
import os
import lightgbm as lgb

class LightGBMInference:
    """
    GCSからLightGBMテキスト形式モデル（lgbm_model.txt）をダウンロードし、推論するクラス
    """
    def __init__(self, bucket_name, model_blob_path, local_model_path="lgbm_model.txt"):
        self.bucket_name = bucket_name
        self.model_blob_path = model_blob_path
        self.local_model_path = local_model_path
        self.model = None

    def download_model(self):
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(self.model_blob_path)
        blob.download_to_filename(self.local_model_path)

    def load_model(self):
        if not os.path.exists(self.local_model_path):
            self.download_model()
        self.model = lgb.Booster(model_file=self.local_model_path)

    def predict(self, X):
        if self.model is None:
            self.load_model()
        return self.model.predict(X)

    def predict_proba(self, X):
        if self.model is None:
            self.load_model()
        # LightGBM Boosterのpredictで確率を返す（binaryの場合）
        return self.model.predict(X)
