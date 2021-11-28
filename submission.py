import os
import traceback
from datetime import datetime

import scipy.sparse as sps

from Evaluation.Evaluator import EvaluatorHoldout
from Recommenders.Incremental_Training_Early_Stopping import Incremental_Training_Early_Stopping
from Recommenders.Recommender_import_list import *
from reader import load_urm, load_icm, load_target
from run_all_algorithms import _get_instance

res_dir = 'result_experiments/csv'
output_root_path = "./result_experiments/"

recommender_class_list = [
    # ItemKNNCBFRecommender,
    # ItemKNN_CFCBF_Hybrid_Recommender,
    SLIMElasticNetRecommender,  # slow to train, good
    # UserKNNCFRecommender,
    # IALSRecommender, # good
    # MatrixFactorization_BPR_Cython,
    # MatrixFactorization_FunkSVD_Cython, # fix low values
    # MatrixFactorization_AsySVD_Cython, # fix low values
    # EASE_R_Recommender, # fix low values
    # ItemKNNCFRecommender,
    # P3alphaRecommender,
    # SLIM_BPR_Python,
    # RP3betaRecommender, # good
    # PureSVDRecommender,
    # NMFRecommender,

    # LightFMCFRecommender,
    # LightFMItemHybridRecommender,
]

# If directory does not exist, create
if not os.path.exists(output_root_path):
    os.makedirs(output_root_path)

logFile = open(output_root_path + "submission_all_algorithms.txt", "a")


def create_csv(target_ids, results, rec_name):
    exp_dir = os.path.join(res_dir, rec_name)
    if not os.path.exists(exp_dir):
        os.makedirs(exp_dir)

    csv_fname = 'results_' + datetime.now().strftime('%b%d_%H-%M-%S') + '.csv'

    with open(os.path.join(exp_dir, csv_fname), 'w') as f:
        f.write('user_id,item_list\n')
        for target_id, result in zip(target_ids, results):
            f.write(str(target_id) + ', ' + ' '.join(map(str, result)) + '\n')


def run_prediction_all_recommenders(URM_all, ICM_all):
    evaluator = EvaluatorHoldout(URM_all, cutoff_list=[10], exclude_seen=True)

    earlystopping_keywargs = {"validation_every_n": 2,
                              "stop_on_validation": True,
                              "evaluator_object": evaluator,
                              "lower_validations_allowed": 3,
                              "validation_metric": "MAP",
                              }

    for recommender_class in recommender_class_list:

        try:
            print("Algorithm: {}".format(recommender_class.RECOMMENDER_NAME))
            recommender_object = _get_instance(recommender_class, URM_all, ICM_all)

            if isinstance(recommender_object, Incremental_Training_Early_Stopping):
                fit_params = {"epochs": 15, **earlystopping_keywargs}
            elif isinstance(recommender_object, SLIMElasticNetRecommender):
                fit_params = {"topK": 463, 'l1_ratio': 0.0014760781357350578, 'alpha': 0.8618057479552595}
            else:
                fit_params = {}

            recommender_object.fit(**fit_params)

            item_list = recommender_object.recommend(target_ids, cutoff=10, remove_seen_flag=True)
            create_csv(target_ids, item_list, recommender_class.RECOMMENDER_NAME)

        except Exception as e:
            traceback.print_exc()
            logFile.write("Algorithm: {} - Exception: {}\n".format(recommender_class.RECOMMENDER_NAME, str(e)))
            logFile.flush()


# Method to create prediction using a saved best model of a specific recommender class

def run_prediction_best_saved_model(URM_all, ICM_all):
    # ******** set here the recommender you want to use
    recommender_object = P3alphaRecommender(URM_all)

    # rec_best_model_last.zip is the output of the run_hyperparameter_search (one best model for each rec class)
    recommender_object.load_model(output_root_path, file_name=recommender_object.RECOMMENDER_NAME + "_best_model.zip")

    # added for prediction
    item_list = recommender_object.recommend(target_ids, cutoff=10, remove_seen_flag=True)
    create_csv(target_ids, item_list, recommender_object.RECOMMENDER_NAME)


if __name__ == '__main__':
    URM_all, user_id_unique, item_id_unique = load_urm()
    ICM_genre = load_icm("data_ICM_genre.csv", weight=1)
    ICM_subgenre = load_icm("data_ICM_subgenre.csv", weight=1)
    ICM_channel = load_icm("data_ICM_channel.csv", weight=1)
    ICM_event = load_icm("data_ICM_event.csv", weight=1)
    target_ids = load_target()

    ICM_all = sps.hstack([ICM_genre, ICM_subgenre, ICM_channel, ICM_event]).tocsr()

    run_prediction_all_recommenders(URM_all, ICM_all)
