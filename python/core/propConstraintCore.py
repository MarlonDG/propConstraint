import mbMayaApi
import maya.cmds

MAIN_POSITION_CTRL = 'Main_position_ctrl'
OBJECT_NOT_ACCEPTED = ('camera')
DESIRED_CONTROL_ATTRIBUTE = 'ParentAttr'


class PropConstraint(object):

    def getReferencesFromScene(self):
        """
        Gets the references in the scene.

        Returns:
            dict: Asset namespace and the reference path.
        """
        sceneReferences = {}

        for referenceName in maya.cmds.ls(type="reference"):
            if OBJECT_NOT_ACCEPTED in referenceName:
                continue

            if referenceName.count("_") >= 4:
                filepath = ""
                try:
                    filepath = maya.cmds.referenceQuery(referenceName, filename=True)
                    namespace = maya.cmds.file(filepath, namespace=True, query=True)

                # when reference is not loaded, we get runtime error, just in case
                except RuntimeError:
                    namespace = referenceName.replace("RN", "")

                sceneReferences[namespace] = filepath

        return sceneReferences

    def getSelectedItemsNameSpace(self):
        """
        Get the namespace of the selected objects.

        Return:
            list [str]: Selected items
        """
        selectedItems = maya.cmds.ls(selection=True)
        selectedItemsList = []

        for node in selectedItems:
            if node.namespace in selectedItemsList:
                continue
            selectedItemsList.append(node.namespace)
        return selectedItemsList


    @staticmethod
    def getSpaceSwitchCtrlsByNamespace(inPropNamespaceList,
                                      inCharacterNamespaceList):
        """
        Get the space switch controls of the prop from namespace.

        Args:
            inPropNamespaceList(list), name spaces to get the character controls from.
            inCharacterNamespaceList(list), name spaces to get the target controls from.

        Returns:
            dict, {propName with namespace:[character target controls with namespace]}

        """

        controlData = {}

        for targetNamespace in inPropNamespaceList:
            nodesInSceneByNameSpace = list(mbMayaApi.MBNode().getNodesByNamespace(targetNamespace))

            if not nodesInSceneByNameSpace:
                return

            for mbNode in nodesInSceneByNameSpace:
                if not mbNode.hasAttribute(DESIRED_CONTROL_ATTRIBUTE):
                    continue

                constraintToDelete = []
                connectedConstraintList = list(mbMayaApi.MBTransform(mbNode).getConstraints())
                if connectedConstraintList:
                    for constraint in connectedConstraintList:
                        constraintToDelete.append(constraint.name)
                    maya.cmds.delete(constraintToDelete)

                # Control with namespace.
                controlFullName = mbNode.fullName

                # Control without namespace.
                controlName = mbNode.name

                # Out Value of the control.
                controlValue = mbNode[DESIRED_CONTROL_ATTRIBUTE].value

                for objectNameSpace in inCharacterNamespaceList:

                    # Add the namespace to controls of the destination
                    destinationControl = '{0}{1}'.format(objectNameSpace, controlName)
                    childControl = '{0}{1}'.format(objectNameSpace, controlValue)

                    targetList = [destinationControl, childControl]

                    if not maya.cmds.objExists(destinationControl):
                        targetList.remove(destinationControl)

                    elif not maya.cmds.objExists(childControl):
                        targetList.remove(childControl)

                    controlData.setdefault(controlFullName, targetList)

        return controlData

    @staticmethod
    def setSpaceSwitchDefaultPosition(inSpaceSwitchDataDict):

        """
        Set the spaceSwitch of the prop(s) controls in the default position to pose it.

        Args:
            inSpaceSwitchDataDict(dict), SpaceSwitch controls from the prop and the character control.
            Ex: {mlb_prp_genericbackpack_rig_main:l__shoulder_parent__ctrl__: ['mlb_chr_marinette_rig_casual_0:l__arm__shoulder__ctrl__']}

        """

        if not inSpaceSwitchDataDict:
            return

        for propCtrl in inSpaceSwitchDataDict:

            # Get the Global control of the "prop"
            propElementPositionCtrl = '{0}:{1}'.format(mbMayaApi.MBNode(propCtrl).namespace,
                                                       MAIN_POSITION_CTRL)

            # Get the Global control of the "character"
            characterElementPositionCtrl = '{0}:{1}'.format(
                                            mbMayaApi.MBNode(inSpaceSwitchDataDict[propCtrl][0]).namespace,
                                            MAIN_POSITION_CTRL)

            if not maya.cmds.objExists(propElementPositionCtrl) or not maya.cmds.objExists(characterElementPositionCtrl):

                print 'No Found {0} or {1}, the setting of controls can not be applied'.format(
                                                                        propElementPositionCtrl,
                                                                        characterElementPositionCtrl)
                return

            characterTranslateMatrix = maya.cmds.xform(characterElementPositionCtrl,
                                                       query=True,
                                                       worldSpace=True,
                                                       translation=True)

            characterRotationMatrix = maya.cmds.xform(characterElementPositionCtrl,
                                                      query=True,
                                                      worldSpace=True,
                                                      rotation=True)

            maya.cmds.xform(propElementPositionCtrl,
                            worldSpace=True,
                            translation=characterTranslateMatrix,
                            rotation=characterRotationMatrix)

            # Set the position of the SpaceSwitch Controls
            maya.cmds.delete(maya.cmds.parentConstraint(inSpaceSwitchDataDict[propCtrl],
                                                        propCtrl,
                                                        maintainOffset=0))




    def createConstraints(self,
                          inTargetNamespaceList,
                          inObjectNamespaceList,
                          inMFnTypeConstraint,
                          translateSkipAxes,
                          rotateSkipAxes):
        """
        Create the constraint of the OnPropConstraint Tool.

        Args:
            inTargetNamespaceList (list[str]), targets namespace.
            inObjectNamespaceList (list[str]), objects namespace.
            inMFnTypeConstraint (int), MFn constraint type.
            translateSkipAxes (list[str]), translate axes to skipped in the constraint.
            rotateSkipAxes (list[str]), rotate axes to skipped in the constraint.
        Returns:
            None.
        """

        for targetNamespace in inTargetNamespaceList:
            nodesInSceneByNameSpace = list(mbMayaApi.MBScene().getNodesByNamespace(targetNamespace))

            if not nodesInSceneByNameSpace:
                return

            for mbNode in nodesInSceneByNameSpace:
                if not mbNode.hasAttribute(DESIRED_CONTROL_ATTRIBUTE):
                    continue

                constraintToDelete = []
                connectedConstraintList = list(mbMayaApi.MBTransform(mbNode).getConstraints())
                if connectedConstraintList:
                    for constraint in connectedConstraintList:
                        constraintToDelete.append(constraint.name)
                    maya.cmds.delete(constraintToDelete)

                # Control without namespace.
                controlName = mbNode.name

                # Out Value of the control.
                controlValue = mbNode[DESIRED_CONTROL_ATTRIBUTE].value

                # Get the Main/Global Control of the character
                propElementPositionCtrl = '{0}:{1}'.format(mbNode.namespace, MAIN_POSITION_CTRL)
                if not maya.cmds.objExists(propElementPositionCtrl):
                    print 'Can Find The ' + MAIN_POSITION_CTRL

                for objectNameSpace in inObjectNamespaceList:

                    # Add the namespace to controls of the destination
                    destinationControl = '{0}{1}'.format(objectNameSpace, controlName)
                    childControl = '{0}{1}'.format(objectNameSpace, controlValue)

                    targetList = [destinationControl, childControl]

                    if not maya.cmds.objExists(destinationControl):
                        targetList.remove(destinationControl)

                    elif not maya.cmds.objExists(childControl):
                        targetList.remove(childControl)

                    onTargetsList = [mbMayaApi.MBNode(target) for target in targetList]

                    objectElementPositionCtrl = '{0}:{1}'.format(objectNameSpace, MAIN_POSITION_CTRL)

                    if not maya.cmds.objExists(objectElementPositionCtrl):
                        print 'Can Find The ' + MAIN_POSITION_CTRL
