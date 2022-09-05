import copy
import numpy as np
import open3d as o3
import probreg

import open3d as o3d

class ProbregTransformation:

    def __init__(self, transformation, sigma2, q):
        self.transformation = transformation
        self.sigma2 = sigma2
        self.q = q

        self.fitness = sigma2
        self.inlier_rmse = q

    def transform(self, cloud):

        result = copy.deepcopy(cloud)
        result.points = self.transformation.transform(result.points)

        return result

class CpdMatcher:

    def __init__(self, tf_type_name='rigid', w=0.0, maxiter=50, tol=0.001, use_cuda=True):
        self.use_cuda = use_cuda
        self.tf_type_name = tf_type_name
        self.w = w
        self.maxiter = maxiter
        self.tol = tol

    def match(self, source, target):

        source = source.voxel_down_sample(voxel_size=1)
        target = target.voxel_down_sample(voxel_size=1)

        res = probreg.cpd.registration_cpd(source, target, tf_type_name=self.tf_type_name, w=self.w, maxiter=self.maxiter, tol=self.tol, use_cuda=self.use_cuda)

        return ProbregTransformation(res.transformation, res.sigma2, res.q)

class FilterregMatcher:

    def __init__(self, objective_type='pt2pt', w=0.0, maxiter=50, tol=0.001):
        self.objective_type = objective_type
        self.w = w
        self.maxiter = maxiter
        self.tol = tol

    def match(self, source, target):

        source = source.voxel_down_sample(voxel_size=1)
        target = target.voxel_down_sample(voxel_size=1)

        res = probreg.filterreg.registration_filterreg(source, target, objective_type=self.objective_type, w=self.w, maxiter=self.maxiter, tol=self.tol)

        return ProbregTransformation(res.transformation, res.sigma2, res.q)