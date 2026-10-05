from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def evaluate(model, X_test, y_test):
    pred = model.predict(X_test)
    rep = classification_report(y_test, pred, output_dict=True, zero_division=0)
    return {"accuracy": accuracy_score(y_test, pred), "macro_precision": rep["macro avg"]["precision"],
            "macro_recall": rep["macro avg"]["recall"], "macro_f1": rep["macro avg"]["f1-score"],
            "weighted_f1": rep["weighted avg"]["f1-score"], "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
            "labels": [str(c) for c in model.classes_]}
