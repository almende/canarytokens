import os
from twisted.python.modules import getModule

thisModule = getModule(__name__)
dataPath = thisModule.filePath.parent().parent()

os.environ["CANARY_WG_PRIVATE_KEY_SEED"] = "iti59nUKwKrE1jbM8scQ4TvQCLCvSXvnW5PO3g8DLLE\\\\\\="
os.environ["CANARY_WEB_IMAGE_UPLOAD_PATH"] = dataPath.child("tests").child("uploads").path
os.environ["CANARY_TEMPLATE_DIR"] = dataPath.child("templates").path
os.environ["CANARY_TEST_REDIS"] = "True"
os.environ["CANARY_DOMAINS"] = "localhost"