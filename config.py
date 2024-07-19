import os

app_base_path = os.getenv("APP_BASE_PATH", default=os.getcwd())
data_base_path = os.path.join(app_base_path, "data")
model_file_path = os.path.join(data_base_path, "model.pkl")

# Ensure the directory exists
os.makedirs(data_base_path, exist_ok=True)

if not os.path.exists(model_file_path):
    raise FileNotFoundError(f"No such file or directory: '{model_file_path}'")

