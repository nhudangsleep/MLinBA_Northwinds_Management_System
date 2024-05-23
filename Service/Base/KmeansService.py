import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class KmeansService:
    def __init__(self, dataframe, num_k=None, is_rfm=None):
        """
        Initialize the KmeansService class with a dataframe, number of clusters (num_k), and an optional is_rfm flag.

        :param dataframe: pd.DataFrame - Data to be clustered
        :param num_k: int - Number of clusters
        :param is_rfm: bool - Optional flag for specific handling (e.g., RFM segmentation)
        """
        self.original_dataframe = dataframe
        self.is_trained = False
        if is_rfm:
            self.dataframe = dataframe[['custId', 'purchaseFrequency', 'totalSpending', 'recency']].copy()
        else:
            self.dataframe = dataframe.copy()

        self.num_k = num_k
        self.is_rfm = is_rfm

    def preprocess_data(self):
        """
        Preprocess the data by standardizing it.

        :return: np.ndarray - Scaled data
        """
        self.scaler = StandardScaler()
        scaled_data = self.scaler.fit_transform(self.dataframe)
        return scaled_data

    def train_model(self):
        """
        Train the KMeans model with the preprocessed data and add cluster labels to the dataframe.
        """
        # Preprocess the data
        data = self.preprocess_data()

        # Initialize and fit the KMeans model
        self.model = KMeans(n_clusters=self.num_k, random_state=42)
        self.model.fit(data)

        # Add cluster labels to the original dataframe
        self.dataframe.loc[self.dataframe.index, 'cluster'] = self.model.labels_
        self.is_trained = True
        self.calculate_elbow_scores()

    def predict(self, new_data):
        """
        Predict the cluster for new data.

        :param new_data: pd.DataFrame - New data to be clustered
        :return: np.ndarray - Predicted cluster labels
        """
        # Preprocess the new data
        scaled_data = self.scaler.transform(new_data)

        # Predict the cluster for new data
        return self.model.predict(scaled_data)

    def get_centroids(self):
        """
        Get the centroids of the clusters.

        :return: np.ndarray - Centroids of the clusters
        """
        return self.model.cluster_centers_

    def get_clustered_data(self):
        """
        Get the original dataframe with an additional column for cluster labels.

        :return: pd.DataFrame - Dataframe with cluster labels
        """
        return self.original_dataframe

    def summarize_clusters(self):
        """
        Provide a summary of the clusters.

        :return: pd.DataFrame - Summary statistics of each cluster
        """
        grouped = self.dataframe.drop(columns=['custId']).groupby('cluster').mean()
        result = grouped.apply(pd.to_numeric).round(2)
        return result

    def calculate_elbow_scores(self, k_range=range(2, 16)):
        """
        Calculate the elbow scores for a range of k values.

        :param k_range: range - Range of k values to calculate elbow scores for
        :return: dict - Dictionary with k values as keys and elbow scores (inertia) as values
        """
        elbow_scores = {}
        data = self.preprocess_data()

        for k in k_range:
            model = KMeans(n_clusters=k, random_state=42)
            model.fit(data)
            elbow_scores[k] = model.inertia_

        return elbow_scores
