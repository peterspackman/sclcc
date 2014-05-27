#!/usr/bin/python
import re
import sys
import numpy as np
import cv2
import matplotlib as mpl
from matplotlib import pyplot as plt
import scipy.stats as stats
import hist  as h
import scipy.spatial.distance
import fastcluster as fc
from scipy.cluster.hierarchy import dendrogram



def spearman_roc(hist1, hist2):
  """ Calculate the Spearman rank-order correlation coefficient from 2 histograms
  This may need to be modified, I'm uncertain whether or not 2 zeroes are ignored
  READ likely that they aren't, as such artificially high correlations are probable
  """ 
  x = hist1.flatten()
  y = hist2.flatten()
  return stats.spearmanr(x,y)

def kendall_tau(hist1, hist2):
  """ Calculate Kendall's Tau from the given histograms"""
  x = hist1.flatten()
  y = hist2.flatten()

  return stats.kendalltau(x,y)



def get_correl_mat(histograms,test=spearman_roc):
  """ SHOULD BE RENAMED TO get_dist_mat
      Given a list of histograms, calculate the distances between them
      and return a NxN redundant array of these distances

      It should be noted that there is a potential inefficiency 
      here as x-> should be the same as y->x, so we could cut cpu time in
      half roughly but cutting out the inefficiency.
  """
  n = len(histograms)

  print "Creating a {0}x{0} matrix using coefficients from {1}".format(n,test.__name__)

  mat = np.zeros( (n,n) )
  
  for i, (H1,x1,y1) in enumerate(histograms):
    for j, (H2,x2,y2) in enumerate(histograms):
      r, p = test(np.array(H1),np.array(H2))
      mat[i][j] = r
  # Becuase these tests give correlations not distances i.e. higher r => closer,
  # we must modify the values to give a distance equivalent

  if test==spearman_roc or test ==kendall_tau:
    # np.round() is used here because of floating point rounding (getting 1.0 - 1.0 != 0.0)
    mat = 1.0 - np.round(mat,decimals=5)
  return mat


def cluster(mat,names,tname):
  """ Takes an NxN array of distances and an array of names with
    the same indices, performs cluster analysis and shows a dendrogram
  """

  # Remove redundant distances from the NxN array (turning it into more of a triangle)
  distArray = scipy.spatial.distance.squareform(mat)
  
  # This is the clustering
  Z = fc.linkage(distArray,method='single',metric='euclidean')
  
  # Create a dendrogram
  R = dendrogram(Z,labels=names)

  # Plot stuff
  plt.xlabel('Compound Name')
  plt.ylabel('Dissimilarity')
  plt.suptitle('Clustering dendrogram of {0} compounds using {1}'.format(len(names),tname))
  plt.show()


