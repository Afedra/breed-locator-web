import os
import pickle
from sklearn.externals import joblib
from skimage.transform import resize
from django.conf import settings
from .data_collector import get_image_data

class DeepMachineLearning():
    
    def __init__(self):
        self.training_data = pickle.load(open(os.path.join(settings.BASE_DIR, "pk_models", 'training_data-13dimHaraFG-PCA.pd.pk'), 'rb'))
        self.breeds = ["ankole","fresian","jersey","zebu"]

    def learn(self, modelDir):
        object_to_classify = get_image_data()
        model = self.load_model(modelDir)
        return self.classify_objects(object_to_classify, model)
        
    def classify_objects(self, object_to_classify, model):
        """
        uses the predict method in the model to predict the category(breed)
        that the image belongs to

        Parameters
        ___________
        objects: Numpy array
        """
        result = model.predict(object_to_classify)
        probabilities = model.predict_proba(object_to_classify)
        result_index = self.breeds.index(result[0])
        prediction_probability = probabilities[0, result_index]
        print(result[0], prediction_probability)
        return result, prediction_probability
        
    def load_model(self, model_dir):
        """
        loads the machine learning using joblib package
        model_dir is the directory for the model
        loading of the model has nothing to do with the classifier used
        """
        model = joblib.load(model_dir)
        return model
