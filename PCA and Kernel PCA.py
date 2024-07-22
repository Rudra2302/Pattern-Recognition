# -*- coding: utf-8 -*-
"""PRML assignment Q1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19H_X3lHR5b96D6wvKqSM5pDyZgRCucnH

Install Datasets from pip
"""

pip install datasets

"""Import the necessary files"""

from datasets import load_dataset

import numpy as np
import matplotlib.pyplot as plt

"""Load the MNIST dataset"""

data=load_dataset("mnist")

"""Show one random image"""

data['train'][1]['image']

"""Make a dataset having 100 images of each digit"""

img = [[] for _ in range(10)] # image array
for i in range(0,60000):
  if(len(img[data['train'][i]['label']])==100): # stop if 100 images have already been  added
    continue
  img[data['train'][i]['label']].append(data['train'][i]['image'])

"""Show one image of each digit"""

fig, axes = plt.subplots(2, 5, figsize=(10, 8)) # 10 images in a 2x5 format
axes=axes.flatten()

for i in range(10):
  ax=axes[i]
  ax.imshow(img[i][0], cmap='gray') # show the image
  ax.axis('off')

plt.tight_layout()
plt.show()

"""Reshape the image array to have 1000 array of 784 greyscale pixel values"""

img_array = np.array(img)
XT = img_array.reshape(-1,28*28) # Flatten 28x28 images into 1D arrays
XT.shape # Check the shape of our data matrix

"""Take the transpose to get our data matrix"""

X = XT.T # The X matrix of d*n size
X.shape # Check the shape of our data matrix

"""Centre the data"""

mean = np.mean(X, axis=1) # Find the mean row wise
XF=X-mean[:, np.newaxis] # Centre the data

"""Find the Covariance matrix"""

cov = XF @ XF.T # Covariance matrix
cov = cov/1000 # C=(XX.T)/n
cov.shape # Check the shape of the covariance matrix

"""Find eigenvectors and eigenvalues"""

lambd, w = np.linalg.eig(cov) # Use the np.linalg library function
lambd = np.real(lambd) # Make them real due to presence of small order complex values
w = np.real(w)

"""Find the total sum of variances(eigenvalues)"""

var_sum=np.sum(lambd) # sum of all entries of the eigenvalue array
var_sum

"""FInd the 1st pincipal component"""

var_max=np.argmax(lambd) # Find the 1st principal component
var_max

"""Sort the eigenvectors in descending order of eigenvalues"""

lambd_ind = np.argsort(lambd)[::-1] # Find sorted indices of eigenvalues
lambd = np.sort(lambd)[::-1] # Sort the eigenvalue array
w = w[:, lambd_ind] # sort eigenvectors accordingly

"""Find variance explained by each principal component in percentages"""

var = lambd/var_sum # Variance explained array
var = var*100 # COnvert to percentages

"""Find no of dimensions required to explain more than 95% variance
130 principal components will be required
"""

sum = 0 # sum of percentages
dims = 0 # no of dimensions

for i in range(784):
  sum += var[i]
  dims += 1
  if sum > 95: # break when sum reaches 95%
    break

dims # print dims

"""Plot the 20 most important principal components"""

fig, axes = plt.subplots(5, 4, figsize=(10, 10)) # 20 images
axes = axes.flatten()
for i in range(20):
  w1=w[:,i].reshape(28,28) # reshape to a 28x28 image
  ax = axes[i]
  ax.imshow(w1, cmap='gray')
  ax.set_title(f"Variance Explained:\n {round(var[i],3)}%") # mention variance explained
  ax.axis('off')

plt.tight_layout()
plt.show()

"""Recreate a random data point using principal components. As we can see, at 130 dimensions we can see the original image being recreated"""

fig, axes = plt.subplots(2, 5, figsize=(10, 10))
axes = axes.flatten()

X0 = XF[:,0] # take a random data point to recreate
X0_new =np.zeros(784)
X0_new = X0_new + mean # to remove the effect of centering
a=0
for i in range(0,784):
  const=X0.T @ w[:,i]
  w_new = w[:,i]*const
  X0_new = X0_new + w_new # X = sum((X.T @ wi)*wi)
  if i==9 or i==19 or i==49 or i==79 or i==129 or i==249 or i==349 or i==499 or i==599 or i==783:
    X0_img=X0_new.reshape(28,28) #print the results for 10 values of dimensions
    ax = axes[a]
    a+=1
    ax.imshow(X0_img, cmap='gray')
    ax.set_title(f"Dimensions:\n {i+1}")
    ax.axis('off')


plt.tight_layout()
plt.show()

"""**Kernel PCA**

Define a function for polynomial and radial basis function kernels
"""

def phi(x,y):
  ans = np.dot(x,y) + 1
  ans = ans**4 # degree 2
  return ans

sigma = 10 # variance assumed = 1
def rbf(x,y):
  d = x-y
  temp = d.T @ d
  temp = temp/(2*sigma*sigma)
  ans = np.exp(-temp)
  return ans

"""Calculate the Kernel matrix K"""

K = np.empty((1000,1000))
for i in range(1000):
  for j in range(1000):
    K[i][j] = rbf(X[:,i], X[:,j])

"""Centre K"""

I = np.ones((1000,1000))/1000
Kc = K - (I @ K) - (K @ I) + (I @ K @ I)
Kc

"""Find eigenvalues and eigenvectors"""

nlambda, beta = np.linalg.eig(Kc)
nlambda = np.abs(nlambda) # take abs of the values to avaoid the small negative numbers

"""Find alpha matrix using alpha=beta/sqrt(nlambda)"""

import math
alpha = np.empty((1000,1000)) # initialize

for i in range(1000):
  alpha[:,i] = beta[:,i]/math.sqrt(nlambda[i])

"""Sort alpha in descending order of eigenvalues to get top 2 components"""

nlambda_ind = np.argsort(nlambda)[::-1] # argument sort
nlambda = np.sort(nlambda)[::-1] # sort nlambda
alpha = alpha[:, nlambda_ind] # sort alpha

"""Find projections of all points over top 2 components"""

proj_x = np.empty((1000))
proj_y = np.empty((1000))
for i in range(1000):
  proj_x[i] = Kc[i,:] @ alpha[:,0] # proj = Kc @ alpha
  proj_y[i] = Kc[i,:] @ alpha[:,1]

"""Scatter plot the projection values"""

colors=['blue','red','green','purple','orange','yellow','pink','black','violet','brown']
for i in range(10):
  start = i*100 # starting index
  end = (i+1)*100 # ending index
  plt.scatter(proj_x[start:end], proj_y[start:end], color=colors[i], label=str(i))

plt.title('Radial basis Kernel with sigma=10')
plt.xlabel('Projections on 1st Principal Component')
plt.ylabel('Projections on 2nd Principal Component')
plt.legend(title='Digits')

