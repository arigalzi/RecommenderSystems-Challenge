from Recommenders.BaseSimilarityMatrixRecommender import BaseItemSimilarityMatrixRecommender
from Recommenders.Recommender_utils import check_matrix
from Recommenders.GraphBased import P3alphaRecommender
from Recommenders.MatrixFactorization import PureSVDRecommender
from Recommenders.DataIO import DataIO
import numpy as np


class ScoresHybridP3alphaPureSVD(BaseItemSimilarityMatrixRecommender):
    """ ItemKNNScoresHybridRecommender
    Hybrid of two prediction scores R = R1*alpha + R2*(1-alpha)
    NB: Rec_1 is itemKNNCF, Rec_2 is userKNNCF
    """

    RECOMMENDER_NAME = "SHP3alphaPureSVD"

    def __init__(self, URM_train):
        super(ScoresHybridP3alphaPureSVD, self).__init__(URM_train)

        self.URM_train = check_matrix(URM_train.copy(), 'csr')
        self.P3alpha = P3alphaRecommender.P3alphaRecommender(URM_train)
        self.svd = PureSVDRecommender.PureSVDRecommender(URM_train)

    def fit(self, topK_P=991, alpha_P=0.4705816992313091, normalize_similarity_P=False, alpha=0.5, num_factors=340,
            norm_scores=True):
        self.alpha = alpha
        self.norm_scores = norm_scores
        self.P3alpha.fit(topK=topK_P, alpha=alpha_P, normalize_similarity=normalize_similarity_P)
        self.svd.fit(num_factors=num_factors)


    def _compute_item_score(self, user_id_array, items_to_compute=None):
        """
        URM_train and W_sparse must have the same format, CSR
        :param user_id_array:
        :param items_to_compute:
        :return:
        """

        item_scores1 = self.P3alpha._compute_item_score(user_id_array, items_to_compute)
        item_scores2 = self.svd._compute_item_score(user_id_array, items_to_compute)

        if self.norm_scores:
            mean1 = np.mean(item_scores1)
            mean2 = np.mean(item_scores2)
            std1 = np.std(item_scores1)
            std2 = np.std(item_scores2)
            item_scores1 = (item_scores1 - mean1) / std1
            item_scores2 = (item_scores2 - mean2) / std2
            '''max1 = item_scores1.max()
            max2 = item_scores2.max()
            item_scores1 = item_scores1 / max1
            item_scores2 = item_scores2 / max2'''
        # print(item_scores1)
        # print(item_scores2)

        item_scores = item_scores1 * self.alpha + item_scores2 * (1 - self.alpha)

        return item_scores

    def save_model(self, folder_path, file_name = None):

        if file_name is None:
            file_name = self.RECOMMENDER_NAME

        self._print("Saving model in file '{}'".format(folder_path + file_name))

        data_dict_to_save = {"Item_Factors_svd": self.svd.ITEM_factors, "User_Factors_svd": self.svd.USER_factors,
                             "norm_scores": self.norm_scores, "W_sparse_P3Alpha": self.P3alpha.W_sparse,
                             "alpha": self.alpha}

        dataIO = DataIO(folder_path=folder_path)
        dataIO.save_data(file_name=file_name, data_dict_to_save = data_dict_to_save)

        self._print("Saving complete")


    def load_model(self, folder_path, file_name = None):

        if file_name is None:
            file_name = self.RECOMMENDER_NAME

        self._print("Loading model from file '{}'".format(folder_path + file_name))

        dataIO = DataIO(folder_path=folder_path)
        data_dict = dataIO.load_data(file_name=file_name)

        for attrib_name in data_dict.keys():
            if attrib_name == "W_sparse_P3Alpha":
                self.P3alpha.W_sparse = data_dict[attrib_name]
            elif attrib_name == "Item_Factors_svd":
                self.svd.ITEM_factors = data_dict[attrib_name]
            elif attrib_name == "User_Factors_svd":
                self.svd.USER_factors = data_dict[attrib_name]
            elif attrib_name == "alpha":
                self.alpha = data_dict[attrib_name]
            elif attrib_name == "norm_scores":
                self.norm_scores = data_dict[attrib_name]

        self._print("Loading complete")
