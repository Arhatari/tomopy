# -*- coding: utf-8 -*-
import numpy as np
import ctypes
import os
import time

libpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib/libgridrec.so'))
libgridrec = ctypes.CDLL(libpath)

class GridrecCStruct(ctypes.Structure):
    """
    The input structure for the C extension library.
    """
    _fields_ = [("numPixels", ctypes.c_int),
                ("numProjections", ctypes.c_int),
                ("numSlices", ctypes.c_int),
                ("sinoScale", ctypes.c_float),
                ("reconScale", ctypes.c_float),
                ("paddedSinogramWidth", ctypes.c_int),
                ("airPixels", ctypes.c_int),
                ("ringWidth", ctypes.c_int),
                ("fluorescence", ctypes.c_int),
                ("reconMethod", ctypes.c_int),
                ("reconMethodTomoRecon", ctypes.c_int),
                ("reconMethodGridrec", ctypes.c_int),
                ("reconMethodBackproject", ctypes.c_int),
                ("numThreads", ctypes.c_int),
                ("slicesPerChunk", ctypes.c_int),
                ("debug", ctypes.c_int),
                ("debugFileName", ctypes.c_byte*256),
                ("geom", ctypes.c_int),
                ("pswfParam", ctypes.c_float),
                ("sampl", ctypes.c_float),
                ("MaxPixSiz", ctypes.c_float),
                ("ROI", ctypes.c_float),
                ("X0", ctypes.c_float),
                ("Y0", ctypes.c_float),
                ("ltbl", ctypes.c_int),
                ("fname", ctypes.c_byte*16),
                ("BP_Method", ctypes.c_int),
                ("BP_MethodRiemann", ctypes.c_int),
                ("BP_MethodRadon", ctypes.c_int),
                ("BP_filterName", ctypes.c_byte*16),
                ("BP_filterSize", ctypes.c_int),
                ("RiemannInterpolation", ctypes.c_int),
                ("RiemannInterpolationNone", ctypes.c_int),
                ("RiemannInterpolationBilinear", ctypes.c_int),
                ("RiemannInterpolationCubic", ctypes.c_int),
                ("RadonInterpolation", ctypes.c_int),
                ("RadonInterpolationNone", ctypes.c_int),
                ("RadonInterpolationLinear", ctypes.c_int)]

class Gridrec():
    def __init__(self,
                 data,
                 sinoScale=1e4,
                 reconScale=1,
                 paddedSinogramWidth=None,
                 airPixels=10,
                 ringWidth=9,
                 fluorescence=0,
                 reconMethod=0,
                 reconMethodTomoRecon=0,
                 numThreads=24,
                 slicesPerChunk=32,
                 debugFileName='',
                 debug=0,
                 geom=0,
                 pswfParam=6,
                 sampl=1,
                 MaxPixSiz=1,
                 ROI=1,
                 X0=0,
                 Y0=0,
                 ltbl=512,
                 fname='shepp',
                 BP_Method=0,
                 BP_filterName='shepp',
                 BP_filterSize=100,
                 RiemannInterpolation=0,
                 RadonInterpolation=0):
        """ 
        Initialize tomography parameters.

        Parameters
        ----------
        numPixels : scalar
            Number of pixels in sinogram row before padding.

        numProjections : scalar
            Number of angles.

        numSlices : scalar
            Number of slices.

        sinoScale : scalar
            Scale factor to multiply sinogram when airPixels=0.

        reconScale : scalar
            Scale factor to multiple reconstruction.

        paddedSinogramWidth : scalar
            Number of pixels in sinogram after padding. If ``None``, it is
            assumed to be the smallest power of two which is higher than
            ``numPixel``.

        airPixels : scalar
            Number of pixels of air to average at each end of sinogram row.

        ringWidth : scalar
            Number of pixels to smooth by when removing ring artifacts.

        fluorescence : scalar
            0=absorption data, 1=fluorescence.

        reconMethod : scalar
            0=tomoRecon, 1=Gridrec, 2=Backproject.

        numThreads : scalar
            Number of threads.

        slicesPerChunk : scalar
            Number of slices per chunk.

        debug : scalar
            Note: if not 0 there may be some memory leakage problems.

        debugFileName : str

        geom : scalar
            0 if array of angles provided; 1,2 if uniform in half,full circle.

        pswfParam : scalar
            PSWF parameter.

        sampl : scalar
            "Oversampling" ratio.

        MaxPixSiz : scalar
            Max pixel size for reconstruction.

        ROI : scalar
            Region of interest (ROI) relative size.

        X0 : scalar
            (X0,Y0)=Offset of ROI from rotation axis in units of
            center-to-edge distance.

        Y0 : scalar
            (X0,Y0)=Offset of ROI from rotation axis in units of
            center-to-edge distance.

        ltbl : scalar
            No. elements in convolvent lookup tables.

        fname : str {shepp, hann, hamm, ramp}
            Name of filter function.

        BP_Method : scalar
            0=Riemann, 1=Radon.

        BP_filterName : str {none, shepp, hann, hamm, ramp}
            Name of filter function.

        BP_filterSize : scalar
            Length of filter.

        RiemannInterpolation :scalar
            0=none, 1=bilinear, 2=cubic.

        RadonInterpolation : scalar
            0=none, 1=linear.
        """
        self.params = GridrecCStruct()
        self.params.numProjections = data.shape[0]
        self.params.numSlices = data.shape[1]
        self.params.numPixels = data.shape[2]
        self.params.sinoScale = sinoScale
        self.params.reconScale = reconScale
        if paddedSinogramWidth is None:
            paddedSinogramWidth = 0
            powerN = 1
            while (paddedSinogramWidth < data.shape[2]):
                paddedSinogramWidth = 2 ** powerN
                powerN += 1
        self.params.paddedSinogramWidth = paddedSinogramWidth
        self.params.airPixels = airPixels
        self.params.ringWidth = ringWidth
        self.params.fluorescence = fluorescence
        self.params.reconMethod = reconMethod
        self.params.reconMethodTomoRecon = 0
        self.params.reconMethodGridrec = 1
        self.params.reconMethodBackproject = 2
        self.params.numThreads = numThreads
        self.params.slicesPerChunk = slicesPerChunk
        self.params.debug = 0
        for m in range(len(map(ord, debugFileName))):
            self.params.debugFileName[m] = map(ord, debugFileName)[m]
        self.params.geom = geom
        self.params.pswfParam = pswfParam
        self.params.sampl = sampl
        self.params.MaxPixSiz = MaxPixSiz
        self.params.ROI = ROI
        self.params.X0 = X0
        self.params.Y0 = Y0
        self.params.ltbl = ltbl
        for m in range(len(map(ord, fname))):
            self.params.fname[m] = map(ord, fname)[m]
        self.params.BP_Method = BP_Method
        self.params.BP_MethodRiemann = 0
        self.params.BP_MethodRadon = 1
        for m in range(len(map(ord, BP_filterName))):
            self.params.BP_filterName[m] = map(ord, BP_filterName)[m]
        self.params.BP_filterSize = BP_filterSize
        self.params.RiemannInterpolation = RiemannInterpolation
        self.params.RiemannInterpolationNone = 0
        self.params.RiemannInterpolationBilinear = 1
        self.params.RiemannInterpolationCubic = 2
        self.params.RadonInterpolation = RadonInterpolation
        self.params.RadonInterpolationNone = 0
        self.params.RadonInterpolationLinear = 1

    def run(self, data, center, theta, slice_no=None):
        """
        Performs reconstruction using the tomographic data.
        
        Gridrec uses the anonymous "gridrec" algorithm (there are
        rumors that it was written by written by Bob Marr and Graham
        Campbell at BNL in 1997). The basic algorithm is based on FFTs
        and interpolations.
        
        Parameters
        ----------
        TomoObj : tomopy data object
            Tomopy data object generated by the Dataset() class.
        
        slice_no : int, optional
            If specified reconstructs only the slice defined by ``slice_no``.
        
        Returns
        -------
        out : ndarray
            Assigns reconstructed values in TomoRecon object as ``recon``.
        """
        # Assign slice_no.
        num_slices = self.params.numSlices
        if slice_no is not None:
            num_slices = 1
        
        # Prepare center for C.
        if np.array(center).size == 1:
            center = np.ones(num_slices) * center

        # We want float32 inputs.
        if not np.any(np.array(data, dtype=np.float32) != data):
            data = np.array(data, dtype='float32')
        if not np.any(np.array(theta, dtype=np.float32) != theta):
            theta = np.array(theta, dtype='float32')
        if not np.any(np.array(center, dtype=np.float32) != center):
            center = np.array(center, dtype='float32')
            
        # Construct the reconstruction object.
        libgridrec.reconCreate(ctypes.byref(self.params),
                            theta.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

        # Prepare input variables by converting them to C-types.
        _num_slices = ctypes.c_int(num_slices)
        datain = np.array(data[:, slice_no, :])
        self.data_recon = np.empty((num_slices,
                                    self.params.numPixels,
                                    self.params.numPixels), dtype='float32')

        # Go, go, go.
        libgridrec.reconRun(ctypes.byref(_num_slices),
                            center.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                            datain.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                            self.data_recon.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        
        # Relax and wait while the reconstruction is running.
        while True:
            recon_complete, slices_remaining = self.poll()
            if recon_complete.value is 1:
                break
            else:
                time.sleep(0.1)
    
        # Destruct the reconstruction object used by the wrapper.
        libgridrec.reconDelete()
    
    def poll(self):
        """ 
        Read the reconstruction status and the number of slices remaining.
        
        Returns
        -------
        recon_complete: scalar
            1 if the reconstruction is complete,
            0 if it is not yet complete.
        
        slices_remaining : scalar
            slices_remaining is the number of slices
            remaining to be reconstructed.
            """
        # Get the shared library
        recon_complete = ctypes.c_int(0)
        slices_remaining = ctypes.c_int(0)
        libgridrec.reconPoll(ctypes.byref(recon_complete),
                            ctypes.byref(slices_remaining))
        return recon_complete, slices_remaining