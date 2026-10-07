from flask import Flask, request, render_template, send_file, redirect, url_for
import pandas as pd
import numpy as np
import os
import joblib
import re
import sqlite3
from lime import lime_tabular

app = Flask(__name__)

model = joblib.load("Models/Voting_model.sav")

SENSOR_ORDER = ['1', '7', '17', '4', '14', '19', '13', '18', '3', '16', '6', '8', '12', '11', '21', '20', '15', '9', '5', '10']
model_feature_names = [f"sensor_{sensor}_std" for sensor in SENSOR_ORDER]
feature_names = [f"Sensor_{sensor}" for sensor in SENSOR_ORDER]

labels = ["No Failure", "Failure"]
X_train = joblib.load("Models/lime_training_data.pkl")

# Mock background used only when loaded LIME data shape is incompatible.
np.random.seed(42)
X_train_mock = np.random.rand(1000, len(feature_names))

if isinstance(X_train, pd.DataFrame):
    if set(model_feature_names).issubset(X_train.columns):
        X_train = X_train[model_feature_names].to_numpy(dtype=float)
    else:
        X_train = X_train.to_numpy(dtype=float)
else:
    X_train = np.asarray(X_train, dtype=float)

if X_train.ndim != 2 or X_train.shape[1] != len(feature_names):
    app.logger.warning(
        "LIME training data shape %s does not match %s features. Using mock data.",
        getattr(X_train, "shape", None),
        len(feature_names),
    )
    X_train = X_train_mock

lime_explainer = lime_tabular.LimeTabularExplainer(
    training_data=X_train,
    feature_names=feature_names,
    class_names=labels,
    mode='classification',
    discretize_continuous=False,
    random_state=42
)


def _predict_proba_for_lime(rows):
    rows = np.asarray(rows, dtype=float)
    rows_df = pd.DataFrame(rows, columns=model_feature_names)
    return model.predict_proba(rows_df)


def generate_lime_explanation(features_scaled):
    features_scaled = np.asarray(features_scaled, dtype=float)
    if features_scaled.ndim == 1:
        features_scaled = features_scaled.reshape(1, -1)
    if features_scaled.shape[1] != len(feature_names):
        raise ValueError(f"Expected {len(feature_names)} features, got {features_scaled.shape[1]}")

    instance = features_scaled[0]
    explanation = lime_explainer.explain_instance(
        data_row=instance,
        predict_fn=_predict_proba_for_lime,
        top_labels=1,
        num_features=len(feature_names)
    )
    return explanation.as_html()

@app.route('/predict', methods=['POST'])
def predict():


    input_features = [float(request.form[name]) for name in model_feature_names]

    features = np.array([input_features], dtype=float)
    features_df = pd.DataFrame(features, columns=model_feature_names)
    
    # Get prediction class
    prediction = model.predict(features_df)[0]
    
    # Get confidence score (probability)
    probabilities = model.predict_proba(features_df)[0]
    confidence_value = probabilities[int(prediction)] * 100
    confidence_score = f"{confidence_value:.2f}%"

    try:
        lime_html = generate_lime_explanation(features)
    except Exception:
        app.logger.exception("LIME explanation generation failed.")
        lime_html = None

    if int(prediction) == 0:
        classification_result = "No Failure"
    else:
        classification_result = "Failure"

    return render_template("result.html", 
                         classification_result=classification_result,
                         confidence_score=confidence_score,
                         lime_html=lime_html)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = request.form.get('user','')
        name = request.form.get('name','')
        email = request.form.get('email','')
        number = request.form.get('mobile','')
        password = request.form.get('password','')

        # Server-side validation
        username_pattern = r'^.{6,}$'
        name_pattern = r'^[A-Za-z ]{3,}$'
        email_pattern = r'^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$'
        mobile_pattern = r'^[6-9][0-9]{9}$'
        password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$'

        if not re.match(username_pattern, username):
            return render_template("signup.html", message="Username must be at least 6 characters.")
        if not re.match(name_pattern, name):
            return render_template("signup.html", message="Full Name must be at least 3 letters, only letters and spaces allowed.")
        if not re.match(email_pattern, email):
            return render_template("signup.html", message="Enter a valid email address.")
        if not re.match(mobile_pattern, number):
            return render_template("signup.html", message="Mobile must start with 6-9 and be 10 digits.")
        if not re.match(password_pattern, password):
            return render_template("signup.html", message="Password must be at least 8 characters, with an uppercase letter, a number, and a lowercase letter.")

        con = sqlite3.connect('signup.db')
        cur = con.cursor()
        cur.execute("SELECT 1 FROM info WHERE user = ?", (username,))
        if cur.fetchone():
            con.close()
            return render_template("signup.html", message="Username already exists. Please choose another.")
        
        cur.execute("insert into `info` (`user`,`name`, `email`,`mobile`,`password`) VALUES (?, ?, ?, ?, ?)",(username,name,email,number,password))
        con.commit()
        con.close()
        return redirect(url_for('login'))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    else:
        mail1 = request.form.get('user','')
        password1 = request.form.get('password','')
        con = sqlite3.connect('signup.db')
        cur = con.cursor()
        cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
        data = cur.fetchone()

        if data == None:
            return render_template("signin.html", message="Invalid username or password.")    

        elif mail1 == 'admin' and password1 == 'admin':
            return render_template("home.html")

        elif mail1 == str(data[0]) and password1 == str(data[1]):
            return render_template("home.html")
        else:
            return render_template("signin.html", message="Invalid username or password.")

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/graphs')
def graphs():
	return render_template('graphs.html')


@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')



if __name__ == '__main__':
    app.run(debug=True)
