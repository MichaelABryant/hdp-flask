import pickle
import pandas as pd

def predict_disease_proba(lst):
    features = [
        'age',
        'sex',
        'cp',
        'trestbps',
        'chol',
        'fbs',
        'restecg',
        'thalach',
        'exang',
        'oldpeak',
        'slope',
        'ca',
        'thal'
        ]
    df = pd.DataFrame(lst).T
    df.columns = features
    
    numerical = [
        'age',
        'trestbps',
        'chol',
        'thalach',
        'oldpeak',
    ]
    
    categorical = [
        'sex',
        'cp',
        'fbs',
        'restecg',
        'exang',
        'slope',
        'ca',
        'thal'
    ]
    
    imputer = pickle.load(open('/home/mbryant/Documents/portfolio-projects/heart-disease-prediction/deployment/app/static/simple_imputer.pkl', 'rb'))
    df = pd.DataFrame(imputer.transform(df), columns=features)
    
    encoder = pickle.load(open('/home/mbryant/Documents/portfolio-projects/heart-disease-prediction/deployment/app/static/one_hot_encoder.pkl', 'rb'))
    df_enc = encoder.transform(df[categorical])
    df_enc = pd.DataFrame(df_enc, columns=encoder.get_feature_names(categorical))
    df = pd.concat([df[numerical], df_enc], axis=1)
    
    scaler = pickle.load(open('/home/mbryant/Documents/portfolio-projects/heart-disease-prediction/deployment/app/static/standard_scaler.pkl', 'rb'))
    df[numerical] = scaler.transform(df[numerical])
    
    model = pickle.load(open('/home/mbryant/Documents/portfolio-projects/heart-disease-prediction/deployment/app/static/logistic_regression.pkl', 'rb'))
    return model.predict_proba(df) 
