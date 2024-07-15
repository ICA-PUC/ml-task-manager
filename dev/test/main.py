'''
pandas version: 1.5.3
scikit-learn version: 1.2.2
'''
import os
import pickle
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer


def main(**kwargs):
    print("reading input...")
    df = pd.read_csv(kwargs['input_path'])

    X = df.drop('income', axis=1)
    y = df['income'].apply(lambda x: 1 if x == '>50K' else 0)

    print("splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Construir o pipeline de pre-processamento para as variaveis numericas e categoricas
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object']).columns

    print("building pipeline...")
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)])

    # Criar o pipeline do modelo
    model = Pipeline(steps=[('preprocessor', preprocessor),
                            ('classifier', LogisticRegression())])

    print("training...")
    model.fit(X_train, y_train)

    # Avaliacao do modelo
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Model accuracy: {accuracy:.4f}')

    pickle_path = os.path.join(kwargs['output_path'], 'model.pkl')
    print("saving data to", pickle_path)
    with open(pickle_path, 'wb') as f:
        pickle.dump(model, f)



if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Sample sklearn code.")
    parser.add_argument("input_path", type=str, help="Path to the input .csv file.")
    parser.add_argument("output_path", type=str, help="Path to where the output .pkl file should be saved.")    
    args = parser.parse_args()

    main(input_path=args.input_path, output_path=args.output_path)