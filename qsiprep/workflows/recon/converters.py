
"""Handle merging and spliting of DSI files."""
import numpy as np
import os
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as niu
import os.path as op
import nibabel as nb
from nipype.interfaces.base import (BaseInterfaceInputSpec, TraitedSpec, File, SimpleInterface,
                                    InputMultiObject, OutputMultiObject, traits, isdefined)
from nipype.utils.filemanip import fname_presuffix
import logging
from dipy.core.geometry import cart2sphere
from dipy.direction import peak_directions
from dipy.core.sphere import HemiSphere
import subprocess
from scipy.io.matlab import loadmat, savemat
from pkg_resources import resource_filename as pkgr
from qsiprep.interfaces.converters import FODtoFIBGZ
from qsiprep.interfaces.bids import QsiprepOutput, ReconDerivativesDataSink
qsiprep_output_names = QsiprepOutput().output_spec.class_editable_traits()


LOGGER = logging.getLogger('nipype.workflow')
ODF_COLS = 20000  # Number of columns in DSI Studio odf split


def init_mif_to_fibgz_wf(name="mif_to_fibgz", output_suffix="", params={}):
    inputnode = pe.Node(niu.IdentityInterface(fields=qsiprep_output_names + ["mif_file"]),
                        name="inputnode")
    outputnode = pe.Node(
        niu.IdentityInterface(fields=['fib_file']), name="outputnode")
    workflow = pe.Workflow(name=name)
    convert_to_fib = pe.Node(FODtoFIBGZ(), name="convert_to_fib")
    workflow.connect([
        (inputnode, convert_to_fib, [('mif_file', 'mif_file')]),
        (convert_to_fib, outputnode, [('fib_file', 'fib_file')])
    ])
    return workflow