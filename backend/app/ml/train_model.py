"""
Train JobSense ML model.

Model:
Job Description -> Job Function

Algorithm:
TF-IDF + Multinomial Naive Bayes
"""

import glob
import json
import os
import sys

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

from .preprocess import clean_frame
from .evaluate import evaluate


# --------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)


# --------------------------------------------------
# MODEL ARTIFACTS
# --------------------------------------------------

ART = os.path.join(
    os.path.dirname(__file__),
    "artifacts"
)


# --------------------------------------------------
# FIND COLUMN
# --------------------------------------------------

def pick(cols, hints):

    for hint in hints:

        for col in cols:

            if hint in col.lower():

                return col

    return None


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

def main():

    print("\n========================================")
    print("       JOBSENSE ML MODEL TRAINING")
    print("========================================\n")


    # --------------------------------------------------
    # FIND DATASET
    # --------------------------------------------------

    files = [
        f
        for f in glob.glob(
            os.path.join(
                ROOT,
                "dataset",
                "*"
            )
        )
        if f.lower().endswith(
            (".csv", ".xlsx")
        )
    ]


    if not files:

        sys.exit(
            "ERROR: No .csv/.xlsx file found inside dataset/"
        )


    path = files[0]


    print("Dataset:")
    print(path)


    # --------------------------------------------------
    # READ DATASET
    # --------------------------------------------------

    if path.lower().endswith(".csv"):

        df = pd.read_csv(
            path,
            encoding_errors="ignore"
        )

    else:

        df = pd.read_excel(path)


    print("\nDataset shape:")
    print(df.shape)


    print("\nColumns:")
    print(list(df.columns))


    # --------------------------------------------------
    # FIND TEXT COLUMN
    # --------------------------------------------------

    text_col = pick(
        df.columns,
        (
            "description",
            "job_desc",
            "text"
        )
    )


    # Target column
    target_col = "function"


    if text_col is None:

        sys.exit(
            "ERROR: Could not find the job description column."
        )


    if target_col not in df.columns:

        sys.exit(
            "ERROR: 'function' column was not found."
        )


    print("\n----------------------------------------")
    print("Training configuration")
    print("----------------------------------------")

    print(
        "Text column   :",
        text_col
    )

    print(
        "Target column :",
        target_col
    )


    # --------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------

    df = clean_frame(
        df,
        text_col,
        target_col
    )


    print("\nAfter cleaning:")
    print(df.shape)


    # --------------------------------------------------
    # CHECK CLASS COUNTS
    # --------------------------------------------------

    counts = df[target_col].value_counts()


    print("\nOriginal function categories:")
    print(len(counts))


    # Keep classes having at least 10 samples
    valid_classes = counts[
        counts >= 10
    ].index


    df = df[
        df[target_col].isin(
            valid_classes
        )
    ].copy()


    counts = df[target_col].value_counts()


    print("\nCategories used for training:")
    print(len(counts))


    print("\nClass distribution:")
    print(counts)


    if len(counts) < 2:

        sys.exit(
            "ERROR: Need at least 2 job-function classes."
        )


    # --------------------------------------------------
    # CHECK CLASS IMBALANCE
    # --------------------------------------------------

    ratio = (
        counts.max()
        /
        counts.min()
    )


    balanced = ratio > 2


    print("\nClass imbalance ratio:")
    print(
        round(
            ratio,
            2
        )
    )


    print(
        "Class imbalance detected:",
        balanced
    )


    # --------------------------------------------------
    # TRAIN / TEST SPLIT
    # --------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        df[text_col],

        df[target_col],

        test_size=0.20,

        stratify=df[target_col],

        random_state=42
    )


    print(
        "\nTraining samples :",
        len(X_train)
    )


    print(
        "Testing samples  :",
        len(X_test)
    )


    # --------------------------------------------------
    # TF-IDF
    # --------------------------------------------------

    print(
        "\nCreating TF-IDF features..."
    )


    vectorizer = TfidfVectorizer(

        max_features=30000,

        ngram_range=(1, 2),

        min_df=2,

        max_df=0.95,

        sublinear_tf=True
    )


    X_train_tfidf = vectorizer.fit_transform(
        X_train
    )


    X_test_tfidf = vectorizer.transform(
        X_test
    )


    print(
        "TF-IDF feature shape:",
        X_train_tfidf.shape
    )


    # --------------------------------------------------
    # TRAIN MULTINOMIAL NAIVE BAYES
    # --------------------------------------------------

    print(
        "\nTraining Multinomial Naive Bayes..."
    )


    model = MultinomialNB(
        alpha=0.1
    )


    model.fit(
        X_train_tfidf,
        y_train
    )


    print(
        "Training completed."
    )


    # --------------------------------------------------
    # EVALUATE
    # --------------------------------------------------

    print(
        "\nEvaluating model..."
    )


    metrics = evaluate(

        model,

        X_test_tfidf,

        y_test
    )


    metrics.update(

        train_samples=len(X_train),

        test_samples=len(X_test),

        num_classes=len(counts),

        class_weight_balanced=False,

        text_column=text_col,

        target_column=target_col,

        algorithm="Multinomial Naive Bayes",

        vectorizer="TF-IDF"
    )


    print(
        "\n========================================"
    )

    print(
        "             MODEL RESULTS"
    )

    print(
        "========================================"
    )


    for key, value in metrics.items():

        if key not in (
            "confusion_matrix",
            "labels"
        ):

            print(
                f"{key}: {value}"
            )


    # --------------------------------------------------
    # CREATE ARTIFACT DIRECTORY
    # --------------------------------------------------

    os.makedirs(
        ART,
        exist_ok=True
    )


    # --------------------------------------------------
    # FILE PATHS
    # --------------------------------------------------

    vectorizer_path = os.path.join(

        ART,

        "tfidf_vectorizer.pkl"
    )


    model_path = os.path.join(

        ART,

        "job_role_model.pkl"
    )


    metrics_path = os.path.join(

        ART,

        "metrics.json"
    )


    # --------------------------------------------------
    # SAVE VECTORIZER
    # --------------------------------------------------

    joblib.dump(

        vectorizer,

        vectorizer_path
    )


    # --------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------

    joblib.dump(

        model,

        model_path
    )


    # --------------------------------------------------
    # SAVE METRICS
    # --------------------------------------------------

    with open(

        metrics_path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            metrics,

            f,

            indent=2,

            default=str
        )


    # --------------------------------------------------
    # SUCCESS
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "         MODEL SAVED SUCCESSFULLY"
    )

    print(
        "========================================"
    )


    print(
        "\nAlgorithm:"
    )

    print(
        "Multinomial Naive Bayes + TF-IDF"
    )


    print(
        "\nVectorizer:"
    )

    print(
        vectorizer_path
    )


    print(
        "\nModel:"
    )

    print(
        model_path
    )


    print(
        "\nMetrics:"
    )

    print(
        metrics_path
    )


    print(
        "\nTraining finished successfully!" 
    )


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    main()