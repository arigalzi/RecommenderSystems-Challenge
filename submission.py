import os
from datetime import datetime

from Recommenders.Hybrids.HybridRatings_IALS_hybrid_EASE_R_hybrid_SLIM_Rp3 import \
    HybridRatings_IALS_hybrid_EASE_R_hybrid_SLIM_Rp3
from Recommenders.Hybrids.MultiRecommender import MultiRecommender
from Recommenders.Recommender_import_list import *
from reader import load_urm, load_target, load_icm

res_dir = 'result_experiments/csv'
output_root_path = "./result_experiments/"

# If directory does not exist, create
if not os.path.exists(output_root_path):
    os.makedirs(output_root_path)


def create_csv(target_ids, results, rec_name):
    exp_dir = os.path.join(res_dir, rec_name)
    if not os.path.exists(exp_dir):
        os.makedirs(exp_dir)

    csv_fname = 'results_' + datetime.now().strftime('%b%d_%H-%M-%S') + '.csv'

    with open(os.path.join(exp_dir, csv_fname), 'w') as f:
        f.write('user_id,item_list\n')
        for target_id, result in zip(target_ids, results):
            f.write(str(target_id) + ', ' + ' '.join(map(str, result)) + '\n')


def run_prediction_on_target(URM_all, target_ids):
    recommender_object = HybridRatings_IALS_hybrid_EASE_R_hybrid_SLIM_Rp3(URM_all)

    fit_params = { 'alpha': 0.9560759641998946, 'beta': 0.7550858561550403, 'gamma': 0.5227204586158875, 'alpha1': 0.9739242060693925, 'beta1': 0.32744235125291515, 'topK1': 837}
    # fit_params = {'weight_array': [0.95, 0.09, 0.25, 0.4, 0.2]}
    recommender_object.fit(**fit_params)
    # recommender_object.save_model(output_root_path, file_name="hybridsimilarityslimrp3withstack.zip")

    # if isinstance(recommender_object, SLIMElasticNetRecommender):
    #     fit_params = {'topK': 742, 'l1_ratio': 0.0004826899479303845, 'alpha': 0.12121987754356242}
    # elif isinstance(recommender_object, IALSRecommender):
    #     fit_params = {'num_factors': 167, 'epochs': 25, 'confidence_scaling': 'log',
    #                   'alpha': 2.7491082249169008, 'epsilon': 0.2892328524505224, 'reg': 0.0003152844014605245}
    # elif isinstance(recommender_object, ScoresHybridRP3betaKNNCBF):
    #     fit_params = {'topK_P': 479, 'alpha_P': 0.66439892057927, 'normalize_similarity_P': False, 'topK': 1761,
    #                   'shrink': 4028, 'similarity': 'tversky', 'normalize': True, 'alpha': 0.9435088940853401,
    #                   'beta_P': 0.38444510929214876, 'feature_weighting': 'none'}
    # elif isinstance(recommender_object, Hybrid_SlimElastic_Rp3):
    #     fit_params = {'alpha': 0.9}
    # elif isinstance(recommender_object, Hybrid_SlimElastic_Rp3_PureSVD):
    #     fit_params = {'alpha': 0.9087371327370033, 'beta': 0.02399161350891344, 'gamma': 0.24457608798347447}
    # elif isinstance(recommender_object, HybridSimilarity_SLIM_Rp3):
    #     fit_params = {'alpha': 0.9610229519605884, 'topK': 1199}
    # elif isinstance(recommender_object, PureSVDRecommender):
    #     fit_params = {'num_factors': 28}
    # elif isinstance(recommender_object, HybridSimilarity_withGroupedusers):
    #     fit_params = {'alpha': 0.979326712891909, 'topK': 1349}
    # elif isinstance(recommender_object, HybridRatings_SLIM_PureSVD):
    #     fit_params = {'alpha': 0.95}
    # elif isinstance(recommender_object, HybridRatings_IALS_hybrid_EASE_R_hybrid_SLIM_Rp3):
    #     fit_params = {'alpha': 0.95}
    # elif isinstance(recommender_object, MultiRecommender):
    #     fit_params = {'weights': [0.95, 0.09, 0.25, 0.4, 0.2]}  # [slim, rp3, ease_r, ials, pure_svd]
    # else:
    #     fit_params = {}

    item_list = recommender_object.recommend(target_ids, cutoff=10)
    create_csv(target_ids, item_list, recommender_object.RECOMMENDER_NAME)


# Method to create prediction using a saved best model of a specific recommender class

def run_prediction_best_saved_model(URM_all, ICM=None):
    # ******** set here the recommender you want to use
    # recommender_object = SLIMElasticNetRecommender(URM_all)
    recommender_object = EASE_R_Recommender(URM_all)

    # rec_best_model_last.zip is the output of the run_hyperparameter_search (one best model for each rec class)
    # recommender_object.load_model(output_root_path, file_name=recommender_object.RECOMMENDER_NAME + "_best_model.zip")

    # recommender_object.load_model(output_root_path, file_name="slimelastic_urmall_453.zip")
    recommender_object.load_model(output_root_path, file_name="EASE_R_Recommender_best_model.zip")

    # added for prediction
    item_list = recommender_object.recommend(target_ids, cutoff=10, remove_seen_flag=True)
    create_csv(target_ids, item_list, recommender_object.RECOMMENDER_NAME)


if __name__ == '__main__':
    URM_all, user_id_unique, item_id_unique = load_urm()
    target_ids = load_target()

    # ICM_channel = load_icm("data_ICM_channel.csv", weight=1)
    ICM_event = load_icm("data_ICM_event.csv", weight=1)
    # ICM_genre = load_icm("data_ICM_genre.csv", weight=1)
    # ICM_subgenre = load_icm("data_ICM_subgenre.csv", weight=1)
    # ICM_all = sps.hstack([ICM_genre, ICM_subgenre, ICM_channel, ICM_event]).tocsr()
    # ICMs = [ICM_genre, ICM_subgenre, ICM_channel, ICM_event, ICM_all]

    run_prediction_on_target(URM_all, target_ids)
    # run_prediction_best_saved_model(URM_all)
