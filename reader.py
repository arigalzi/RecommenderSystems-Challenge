import os

import pandas as pd
import scipy.sparse as sps
import numpy as np

# urm_path = "Data_manager_split_datasets/TVShows/data_train.csv"
# icm_path = "Data_manager_split_datasets/TVShows/"
# target_path = "Data_manager_split_datasets/TVShows/data_target_users_test.csv"
from Evaluation.Evaluator import EvaluatorHoldout


def load_urm():
    urm_path = os.path.join(os.path.dirname(__file__), 'Data_manager_split_datasets/TVShows/data_train.csv')
    df_original = pd.read_csv(filepath_or_buffer=urm_path, sep=',', header=0,
                              dtype={0: np.int32, 1: np.int32, 2: np.int32})

    df_original.columns = ["UserID", "ItemID", "Data"]

    user_id_list = df_original['UserID'].values
    item_id_list = df_original['ItemID'].values
    rating_id_list = df_original['Data'].values

    user_id_unique = np.unique(user_id_list)
    item_id_unique = np.unique(item_id_list)

    csr_matrix = sps.csr_matrix((rating_id_list, (user_id_list, item_id_list)))
    csr_matrix = csr_matrix.astype(dtype=np.int32)
    # print("DataReader:")
    # print("\tLoading the URM:")
    # print("\t\tURM size:" + str(csr_matrix.shape))
    # print("\t\tURM unique users:" + str(user_id_unique.size))
    # print("\t\tURM unique items:" + str(item_id_unique.size))
    # print("\tURM loaded.")

    return csr_matrix, user_id_unique, item_id_unique


def load_target():
    target_path = os.path.join(os.path.dirname(__file__), 'Data_manager_split_datasets/TVShows/data_target_users_test.csv')

    df_original = pd.read_csv(filepath_or_buffer=target_path, sep=',', header=0,
                              dtype={'UserID': np.int32})

    df_original.columns = ['UserID']

    user_id_list = df_original['UserID'].values

    user_id_unique = np.unique(user_id_list)

    # print("DataReader:")
    # print("\tLoading the target users:")
    # print("\t\tTarget size:" + str(user_id_unique.shape))
    # print("\tTarget users loaded.")

    return user_id_unique


def load_icm(icm_file, weight=1):
    icm_path = os.path.join(os.path.dirname(__file__), 'Data_manager_split_datasets/TVShows/')

    df_original = pd.read_csv(filepath_or_buffer=icm_path + icm_file, sep=',', header=0,
                              dtype={'ItemID': np.int32, 'Feature': np.int32, 'Data': np.int32})

    df_original.columns = ['ItemID', 'Feature', 'Data']

    item_id_list = df_original['ItemID'].values
    feature_id_list = df_original['Feature'].values
    data_id_list = df_original['Data'].values * weight

    csr_matrix = sps.csr_matrix((data_id_list, (item_id_list, feature_id_list)))

    return csr_matrix


def load_merged_icm(icm_file, weight=1):
    icm_path = os.path.join(os.path.dirname(__file__), 'Data_manager_split_datasets/TVShows/')

    df_original = pd.read_csv(filepath_or_buffer=icm_path + icm_file, sep=',', header=0,
                              dtype={'ItemID': np.int32, 'Feature': np.int32, 'Data': np.int32})

    item_id_list = df_original['ItemID'].values
    channel_list = df_original['Channel'].values
    event_list = df_original['Event'].values
    genre_list = df_original['Genre'].values
    subgenre_list = df_original['Subgenre'].values

    data_id_list = df_original['Data'].values * weight

    # Error: invalid input format
    csr_matrix = sps.csr_matrix((data_id_list, (item_id_list, channel_list, event_list, genre_list, subgenre_list)))

    return csr_matrix


def load_all_icms():
    ICM_channel = load_icm("data_ICM_channel.csv", weight=1)
    ICM_event = load_icm("data_ICM_event.csv", weight=1)
    ICM_genre = load_icm("data_ICM_genre.csv", weight=1)
    ICM_subgenre = load_icm("data_ICM_subgenre.csv", weight=1)

    return ICM_channel, ICM_event, ICM_genre, ICM_subgenre


# to delete
def load_urm_icm():
    urm, _, _ = load_urm()
    icm = load_icm("data_ICM_subgenre.csv", 1)
    urm_icm = sps.vstack([urm, icm.T])
    urm_icm = urm_icm.tocsr()

    return urm_icm



def group_users_in_urm (URM_train, URM_test, group_to_test):
    n_users = 13650
    n_item = 18059
    cutoff=10

    profile_length = np.ediff1d(sps.csr_matrix(URM_train).indptr)
    print("profile", profile_length, profile_length.shape)

    block_size = int(len(profile_length) * 0.5)
    print("block_size", block_size)

    sorted_users = np.argsort(profile_length)
    print("sorted users", sorted_users)

    group_id = group_to_test
    start_pos = group_id * block_size
    end_pos = min((group_id + 1) * block_size, len(profile_length))

    users_in_group = sorted_users[start_pos:end_pos]

    users_in_group_p_len = profile_length[users_in_group]

    print("Group {}, #users in group {}, average p.len {:.2f}, median {}, min {}, max {}".format(
        group_id,
        users_in_group.shape[0],
        users_in_group_p_len.mean(),
        np.median(users_in_group_p_len),
        users_in_group_p_len.min(),
        users_in_group_p_len.max()))

    users_not_in_group_flag = np.isin(sorted_users, users_in_group, invert=True)
    users_not_in_group = sorted_users[users_not_in_group_flag]

    evaluator_test = EvaluatorHoldout(URM_test, cutoff_list=[cutoff], ignore_users=users_not_in_group)

    return evaluator_test