# import system libs
import pathlib

# log and command
import click

# import data handling tools
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

# custom functions
from data_functions import (
    define_paths,
    define_df,
    split_data,
    create_gens,
    loading_dataset,
)
from plot_functions import plot_confusion_matrix
from model_functions import load_model

# Ignore Warnings
import warnings

warnings.filterwarnings("ignore")


def evaluate_model(test_df, model, train_gen, valid_gen, test_gen):
    ts_length = len(test_df)
    test_batch_size = test_batch_size = max(
        sorted(
            [
                ts_length // n
                for n in range(1, ts_length + 1)
                if ts_length % n == 0 and ts_length / n <= 80
            ]
        )
    )
    test_steps = ts_length // test_batch_size

    train_score = model.evaluate(train_gen, steps=test_steps, verbose=1)
    valid_score = model.evaluate(valid_gen, steps=test_steps, verbose=1)
    test_score = model.evaluate(test_gen, steps=test_steps, verbose=1)
    return train_score, valid_score, test_score


def get_predictions(model, test_gen):
    preds = model.predict(test_gen)
    y_pred = np.argmax(preds, axis=1)
    return preds, y_pred


def save_classification_report(test_gen, y_pred, output_folder_path, classes):
    report = classification_report(
        test_gen.classes, y_pred, target_names=classes, output_dict=True
    )
    df = pd.DataFrame(report).transpose()
    output_filename = pathlib.Path(output_folder_path) / "classification_report.csv"
    df.to_csv(output_filename)
    print(f"Classification Report saved at: {output_filename}")


def save_confusion_matrix(test_gen, y_pred, savepath, normalize=False):
    g_dict = test_gen.class_indices
    classes = list(g_dict.keys())

    # Confusion matrix
    cm = confusion_matrix(test_gen.classes, y_pred)
    plot_confusion_matrix(savepath, cm, classes, normalize=normalize)
    print(f"Confusion matrix saved at: {savepath}")


@click.command(context_settings={"show_default": True})
@click.option("--model_name", help="Name of the model file to load.", required=True)
@click.option(
    "--model_path",
    default="../../models",
    help="Abs or relative path to the models storage folder.",
)
@click.option(
    "--path_to_data",
    default="../../data/processed",
    help="Abs or relative path to the processed data folder are expected.",
)
@click.option(
    "--covid_dataset_processed_name",
    default="COVID-19_masked_features",
    help="Processed dataset name.",
)
@click.option(
    "--save_location",
    default="../../models",
    help="Abs or relative path to figure save location.",
)
@click.option("--batch_size", default=16, help="Size of the batch.")
@click.option(
    "--cm_normalize",
    type=click.Choice(["True", "False"]),
    default="False",
    help="Should the CM be normalized.",
)
def predict_model(
    model_name,
    model_path,
    path_to_data,
    covid_dataset_processed_name,
    save_location,
    batch_size,
    cm_normalize,
):
    """Main function to evaluate the trained model.

    This scripts is meant to be executed in its folder with the command "python3 train_model.py --model_name YourModelName.keras".

    The model's classification report and confusion matrix after evaluation will be saved in the "data/model" folder (save_location argument).

    The predict code was taken and adapted from Ahmed Hafez's work:
    "https://www.kaggle.com/code/ahmedtronic/covid-19-radiology-vgg19-f1-score-95".
    """
    # config
    model_save_path = pathlib.Path(model_path) / model_name
    data_dir = pathlib.Path(path_to_data) / covid_dataset_processed_name

    # load model
    model = load_model(model_save_path)

    # load data
    train_df, valid_df, test_df, train_gen, valid_gen, test_gen = loading_dataset(
        data_dir, batch_size
    )

    # evaluate
    train_score, valid_score, test_score = evaluate_model(
        test_df, model, train_gen, valid_gen, test_gen
    )
    preds, y_pred = get_predictions(model, test_gen)

    # plot
    classes = list(test_gen.class_indices.keys())
    save_classification_report(test_gen, y_pred, save_location, classes)
    cm_normalize = cm_normalize == "True"
    save_confusion_matrix(test_gen, y_pred, save_location, normalize=cm_normalize)


if __name__ == "__main__":
    predict_model()
