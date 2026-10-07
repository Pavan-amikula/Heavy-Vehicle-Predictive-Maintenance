# Heavy Vehicle Predictive Maintenance

**From synthetic sensor telemetry to failure classification and local explanations.**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)

An academic machine learning project that compares individual classifiers with a five-model soft-voting ensemble. A Flask interface accepts sensor statistics and displays failure predictions, probabilities, and LIME explanations.

## Project report and problem-solving context

[Read the predictive-maintenance report](docs/reports/predictive-maintenance-report.pdf), coauthored by **Pavan Kumar Goud Amikula** and **Naga Sreerama Pradyumna Tata** at Blekinge Institute of Technology.

The problem is to classify rare potential failures from sensor features while understanding the cost of missed failures. The report discusses cleaning and aggregation, imbalance handling with SMOTE, comparisons between models, ensemble learning, error-based costs, explainability, and a Flask interface. It establishes coauthorship but does not assign individual implementation tasks.

The report states a 98.5% result for its voting classifier. That is a reported historical experiment, not a newly reproduced result or proof of real-fleet performance. The implementation's synthetic-data scope and explanation caveats below remain important.

## Pipeline

Synthetic telemetry → vehicle-level feature aggregation → train/test split → feature selection → SMOTE on training data → model comparison → soft voting → Flask + LIME.

- Generator: 5,000 vehicles, 50 time steps, 21 sensors, and a configured 7% failure probability.
- Ensemble: Random Forest, XGBoost, Gradient Boosting, LightGBM, and Logistic Regression.
- Evaluation: classification reports, confusion matrices, and a cost function assigning a missed failure ten times the cost of a false alarm.
- Interface: 20 sensor standard-deviation features in the order expected by the saved model.

## Repository guide

| Path | Purpose |
| --- | --- |
| `data.py` | Reproducible synthetic telemetry generator |
| `Notebook.ipynb` | Feature preparation, training, comparisons, and explanations; cell outputs cleared |
| `app.py` | Flask prediction demo |
| `templates/`, `static/` | Interface and saved charts |
| `testcases/samples.csv` | Example sensor inputs |
| `Models/` | Local location for generated model artifacts |

## Run locally

Use a Python environment compatible with the supplied dependency versions. The original environment notes are retained in `requirements.txt`; dependency installation and model training have not been revalidated in this publication.

```bash
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -r requirements.txt
python -m pip install jupyter
python data.py
jupyter notebook Notebook.ipynb
```

Run the notebook from the repository root to create `Models/Voting_model.sav` and `Models/lime_training_data.pkl`. Then run `python app.py` and visit `http://127.0.0.1:5000/home` for the prediction demo. The legacy signup/signin screens need a local `signup.db` with an `info` table; no user database is distributed.

## Scope and limitations

This is a synthetic-data classification experiment, not evidence of performance on real fleet telemetry. It aggregates full vehicle sequences and should not be described as a validated real-time early-warning system. The demo includes legacy authentication code and Flask debug mode; use it locally. The LIME code falls back to mock background data if the training artifact has incompatible dimensions, which limits the meaning of those explanations. Model binaries, generated datasets, the signup database, and the large demo video are excluded from Git.
