"""
Module created to contains the constans variables used in this tool.
"""
import maya.api.OpenMaya

MFN_CONSTRAINT_TYPES_TO_NAME_TYPES = {maya.api.OpenMaya.MFn.kParentConstraint: "parentConstraint",
                                      maya.api.OpenMaya.MFn.kPointConstraint: "pointConstraint",
                                      maya.api.OpenMaya.MFn.kOrientConstraint: "orientConstraint",
                                      }
BASE_TRANSFORM_AXES = ('x',
                       'y',
                       'z')
