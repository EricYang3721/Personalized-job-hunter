# Here contains all the functions for k-means implementation
import graphlab
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from scipy.sparse import csr_matrix
import time
##############################################################################################
# Implementation of k means with random initialization

from distutils.version import StrictVersion
assert (StrictVersion(graphlab.version) >= StrictVersion('1.8.5')), 'GraphLab Create must be version 1.8.5 or later.'

# Initialize centroids
def get_initial_centroids(data, k, seed=None):
    '''Randomly choose k data points as initial centroids'''
    if seed is not None: 
        np.random.seed(seed)
    n = data.shape[0]   
    rand_indices = np.random.randint(0, n, k)   
    centroids = data[rand_indices,:].toarray()
    
    return centroids

# Assigning clusters
from sklearn.metrics import pairwise_distances
def assign_clusters(data, centroids):
    distances_from_centroids = pairwise_distances(data, centroids, metric='euclidean')
    cluster_assignment = np.argmin(distances_from_centroids, axis=1)
    return cluster_assignment

# Revising clusters
def revise_centroids(data, k, cluster_assignment):
    new_centroids = []
    for i in xrange(k):       
        member_data_points = data[cluster_assignment==i]        
        centroid = member_data_points.mean(axis=0)
        centroid = centroid.A1
        new_centroids.append(centroid)
    new_centroids = np.array(new_centroids)   
    return new_centroids

# Assessing convergence
def compute_heterogeneity(data, k, centroids, cluster_assignment):
    
    heterogeneity = 0.0
    for i in xrange(k):      
        member_data_points = data[cluster_assignment==i, :]
        
        if member_data_points.shape[0] > 0:          
            distances = pairwise_distances(member_data_points, [centroids[i]], metric='euclidean')
            squared_distances = distances**2
            heterogeneity += np.sum(squared_distances)
        
    return heterogeneity

# Combine functions into kmeans
def kmeans(data, k, initial_centroids, maxiter, record_heterogeneity=None, verbose=False):
    '''This function runs k-means on given data and initial set of centroids.
       maxiter: maximum number of iterations to run.
       record_heterogeneity: (optional) a list, to store the history of heterogeneity as function of iterations
                             if None, do not store the history.
       verbose: if True, print how many data points changed their cluster labels in each iteration'''
    centroids = initial_centroids[:]
    prev_cluster_assignment = None
    
    for itr in xrange(maxiter):        
        if verbose:
            print(itr, "iteration")
        cluster_assignment = assign_clusters(data, centroids)
   
        centroids = revise_centroids(data, k, cluster_assignment)
        if prev_cluster_assignment is not None and \
          (prev_cluster_assignment==cluster_assignment).all():
            break        
        if prev_cluster_assignment is not None:
            num_changed = sum(abs(prev_cluster_assignment-cluster_assignment))
            if verbose:
                print('    {0:5d} elements changed their cluster assignment.'.format(num_changed))       
        if record_heterogeneity is not None:          
            score = compute_heterogeneity(data, k, centroids, cluster_assignment)
            record_heterogeneity.append(score)        
        prev_cluster_assignment = cluster_assignment[:]        
    return centroids, cluster_assignment
#########################################################################################
# Load data and run k means on dataset
# Load data, extract features
wiki = graphlab.SFrame('people_wiki.gl/')
wiki['tf_idf'] = graphlab.text_analytics.tf_idf(wiki['text'])
def sframe_to_scipy(x, column_name):
    '''
    Convert a dictionary column of an SFrame into a sparse matrix format where
    each (row_id, column_id, value) triple corresponds to the value of
    x[row_id][column_id], where column_id is a key in the dictionary.
       
    Example
    >>> sparse_matrix, map_key_to_index = sframe_to_scipy(sframe, column_name)
    '''
    assert x[column_name].dtype() == dict, \
        'The chosen column must be dict type, representing sparse data.'
        
    # Create triples of (row_id, feature_id, count).
    # 1. Add a row number.
    x = x.add_row_number()
    # 2. Stack will transform x to have a row for each unique (row, key) pair.
    x = x.stack(column_name, ['feature', 'value'])

    # Map words into integers using a OneHotEncoder feature transformation.
    f = graphlab.feature_engineering.OneHotEncoder(features=['feature'])
    # 1. Fit the transformer using the above data.
    f.fit(x)
    # 2. The transform takes 'feature' column and adds a new column 'feature_encoding'.
    x = f.transform(x)
    # 3. Get the feature mapping.
    mapping = f['feature_encoding']
    # 4. Get the feature id to use for each key.
    x['feature_id'] = x['encoded_features'].dict_keys().apply(lambda x: x[0])

    # Create numpy arrays that contain the data for the sparse matrix.
    i = np.array(x['id'])
    j = np.array(x['feature_id'])
    v = np.array(x['value'])
    width = x['id'].max() + 1
    height = x['feature_id'].max() + 1

    # Create a sparse matrix.
    mat = csr_matrix((v, (i, j)), shape=(width, height))

    return mat, mapping
tf_idf, map_index_to_word = sframe_to_scipy(wiki, 'tf_idf')

# Normalize all vectors
from sklearn.preprocessing import normalize
tf_idf = normalize(tf_idf)

# Running k-means on the dataset
start = time.time()
k = 3  # seeting up number of cluster centers
seed_set = 100000 # setting up seed for initialization
heterogeneity = []
initial_centroids = get_initial_centroids(tf_idf, k, seed=seed_set)
centroids, cluster_assignment = kmeans(tf_idf, k, initial_centroids, maxiter=400,
                                       record_heterogeneity=heterogeneity, verbose=True)
# plot_heterogeneity(heterogeneity, k)
end = time.time()
heter = compute_heterogeneity(tf_idf, k, centroids, cluster_assignment)
print ("the total time used is: " + str(end-start))
print("the total heterogeneity is: " + str(heter))