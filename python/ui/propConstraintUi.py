import PySide2.QtWidgets
import PySide2.QtGui
import PySide2.QtCore

import core.propConstraintCore
import core.constants
import propPoseSelector
import maya.api.OpenMaya

ASSET_TYPE_NAME_MAPPING = {'Character': 'chr',
                           'Prop': 'prp'}


class PropConstraintMainWindow(PySide2.QtWidgets.QMainWindow):
    """
    Main window widget of the OnProConstraint Tool.

    Args:
    	inMainToolNameStr (str): The given name for the tool.

    """
    def __init__(self, inMainToolNameStr, parent=None):

        super(PropConstraintMainWindow, self).__init__(parent=parent)

        # Set the main size of the tool
        self.resize(500, 800)

        self.setWindowTitle(inMainToolNameStr)

        self.initCentralWidget()

        # Main Signal
        self.ApplyConstraintButton.clicked.connect(self.applyConstraint)

    def initCentralWidget(self):
        """
        Main Initializer method for the tool, where all the widgets are called to build
        the widget that would be the central widget of the window.

        Returns:
        	 None.
        """

        mainWidget = PySide2.QtWidgets.QWidget()
        mainLayout = PySide2.QtWidgets.QVBoxLayout()
        mainWidget.setLayout(mainLayout)

        # Instance the widgets needed in the tool
        self.characterSelector = ObjectSelectorWidget("Select Character Object : ",
                                                      ASSET_TYPE_NAME_MAPPING['Character'],
                                                      False)

        self.propSelector = ObjectSelectorWidget("Select Prop Object : ",
                                                 ASSET_TYPE_NAME_MAPPING['Prop'],
                                                 True)

        self.constraintTypeSelector = ConstraintTypeSelector()

        self.propPoseSelector = propPoseSelector.PoseSelector()

        self.ApplyConstraintButton = PySide2.QtWidgets.QPushButton("Create Constraint!")


        # Add the widgets
        mainLayout.addWidget(self.characterSelector)
        mainLayout.addWidget(self.propSelector)

        mainLayout.addWidget(self.constraintTypeSelector)
        mainLayout.addWidget(self.propPoseSelector)

        mainLayout.addWidget(self.ApplyConstraintButton)

        self.setCentralWidget(mainWidget)

    # --------------------------
    # ------
    # SLOTS
    # ------
    # --------------------------
    def getPropSelected(self):
        """
        Get the name of the prop selected in the propSelector in the UI.

        Returns:
             list[str]: name(s) of the selected prop.
        """
        return [listWidgetItem.text() for listWidgetItem in self.propSelector.itemsSelectedInList]

    def applyConstraint(self):
        """
        Slot method to apply constraint.

        Returns:
        	bool: True if a constraint was created, False otherwise.

        """

        # characterSelection = self.characterSelector.itemsSelectedInList
        if not self.characterSelector.itemsSelectedInList or not self.propSelector.itemsSelectedInList:
            return False

        characterNameSpaceList = ['{0}:'.format(listWidgetItem.text()) for listWidgetItem in
                              self.characterSelector.itemsSelectedInList]

        propNameSpaceList = ['{0}:'.format(listWidgetItem.text()) for listWidgetItem in
                         self.propSelector.itemsSelectedInList]

        # Instance of the Core class
        propConstraint = core.propConstraintCore.PropConstraint()

        posesFilePathList = list(self.propPoseSelector.listWidget.getDataFromItemSelected())

        if posesFilePathList:
            core.propConstraintCore.loadPropPose(posesFilePathList,
                                          propNameSpaceList,
                                          True)

        # Query the selected constraintType
        selectedMFnConstraint = self.constraintTypeSelector.constraintTypeCombBox.currentData()

        # Define as None the main two undesired axes.
        undesiredTranslteAxes = None
        undesiredRotateAxes = None

        if selectedMFnConstraint == maya.api.OpenMaya.MFn.kParentConstraint:
            undesiredTranslteAxes = list(self.constraintTypeSelector.translateAxisSelected)
            undesiredRotateAxes = list(self.constraintTypeSelector.rotateAxisSelected)

            core.propConstraintCore.createConstraints(propNameSpaceList,
                                               characterNameSpaceList,
                                               selectedMFnConstraint,
                                               undesiredTranslteAxes,
                                               undesiredRotateAxes)

        elif selectedMFnConstraint == maya.api.OpenMaya.MFn.kPointConstraint:
            undesiredTranslteAxes = list(self.constraintTypeSelector.translateAxisSelected)
            core.propConstraintCore.createConstraints(propNameSpaceList,
                                               characterNameSpaceList,
                                               selectedMFnConstraint,
                                               undesiredTranslteAxes,
                                               None)


        else:
            undesiredRotateAxes = list(self.constraintTypeSelector.rotateAxisSelected)

            core.propConstraintCore.createConstraints(propNameSpaceList,
                                               characterNameSpaceList,
                                               selectedMFnConstraint,
                                               None,
                                               undesiredRotateAxes)


class ObjectSelectorWidget(PySide2.QtWidgets.QWidget):
    """
    Provides a fully built object selector for the constraint Manager

    Args:
    	inSelectorType (str): Title for the selector widget, Ex: 'Select Character' or 'Select Prop'
    	inAssetTypeKey (str): Asset type, Ex; 'Character' or 'Select Prop'
		inMultSelection (bool): True for multiselection of the widget, False otherwise.
    """

    def __init__(self, inSelectorType, inAssetTypeKey=None, inMultSelection = False):
        super(ObjectSelectorWidget, self).__init__()

        self.multiSelection = inMultSelection

        self.inAssetTypeStr = inSelectorType
        self.assetTypeKey = inAssetTypeKey

        # Calling the main initializer
        self.initMainSelectorWidget()

    def initMainSelectorWidget(self):
        """
        Main Initializer method of the object selector, where all the widgets are unified to provide.

        Return:
        	None.

        """

        # Main layout of the selector widget
        mainLayout = PySide2.QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        # Add the group box for the parent object and the child object.
        mainLayout.addWidget(self.selectorMainGroupBox(self.inAssetTypeStr))


    def selectorMainGroupBox(self, inTitleStr):
        """
        Provides the main QGroupBox for the object selector with all the widgets needed.

        Args:
        	inTitleStr (str): the title for the QGroupBox, ex; 'Select Character Object' / 'Select Prop Object'

        Return:
        	groupBoxWidget (QGroupBoxWidget): Parent Widget of the  listWidgetAndSelectButton and objectListWidget.
        """
        self.assetTypeStr = inTitleStr

        groupBoxWidget = PySide2.QtWidgets.QGroupBox()
        groupBoxWidget.setTitle(self.assetTypeStr)

        groupBoxLayout = PySide2.QtWidgets.QVBoxLayout()
        groupBoxWidget.setLayout(groupBoxLayout)

        # Add the listWidget with its button.
        groupBoxLayout.addWidget(self.listWidgetAndSelectButton())

        return groupBoxWidget


    def listWidgetAndSelectButton(self):
        """
        Provides the full build of the listWidget and the Select Button, where the namespace of the objects will be.

        Args: No args.

        Return: parentWidget (QWidget); Parent of ListWidget and the Button.
        """
        # Create the QWidget and the Layout where the QListWidget and the Select Button will be attached to.
        parentWidget = PySide2.QtWidgets.QWidget()
        parentLayout = PySide2.QtWidgets.QHBoxLayout(parentWidget)

        # Main QList Widget and Select Button
        self.objectsListWidget = PySide2.QtWidgets.QListWidget()

        if self.multiSelection == False:
            self.objectsListWidget.setSelectionMode(PySide2.QtWidgets.QListWidget.SingleSelection)

        self.selectButton = PySide2.QtWidgets.QPushButton("Select/Reload \n(Asset)")

        parentLayout.addWidget(self.objectsListWidget)
        parentLayout.addWidget(self.selectButton)

        return parentWidget
    # --------------------------
    # ------
    # SLOTS
    # ------
    # --------------------------

    @property
    def itemsSelectedInList(self):
        """
        Gets the items selected

        Returns:
            list [QWidgets], Items selected.
        """
        return self.objectsListWidget.selectedItems()


class ConstraintTypeSelector(PySide2.QtWidgets.QGroupBox):
    """
    This class provides the a QGroupBox that contains the constraint types to select which are:
                                                                                    'Parent Constraint'
                                                                                    'Point  Constraint'
                                                                                    'Orient Constraint'
    """
    def __init__(self):
        super(ConstraintTypeSelector, self).__init__()

        self.setTitle("Select the constraint type:")
        # Instance the main initializer
        self.initMainSelectorWidget()

        # Signals
        self.defineAxisInUse()
        self.constraintTypeCombBox.currentIndexChanged.connect(self.defineAxisInUse)

    def initMainSelectorWidget(self):
        """
        Provides the main widget of the ConstraintsTypeSelector where the types and the axes of the constraints are.

        Args: No Args.

        Return: No Return.
        """
        mainLayout = PySide2.QtWidgets.QVBoxLayout()
        mainLayout.setSpacing(1)

        self.setLayout(mainLayout)

        # Add all the widgets need into the mainLayout
        mainLayout.addLayout(self.constrainTypeComboBox())
        mainLayout.addWidget(self.constraintAxisCheckBoxes())

    def constrainTypeComboBox(self):
        """
        Provides the QComboBox containing the constraint type.

        Args: No Args.

        Return: comboWidget (QComboxBox).
        """
        comboLayout = PySide2.QtWidgets.QVBoxLayout()

        self.constraintTypeCombBox = PySide2.QtWidgets.QComboBox()

        for constraintType, constraintName in core.constants.MFN_CONSTRAINT_TYPES_TO_NAME_TYPES.iteritems():
            self.constraintTypeCombBox.addItem(constraintName, constraintType)
            self.constraintTypeCombBox.setCurrentIndex(1)


        comboLayout.addWidget(self.constraintTypeCombBox)

        return comboLayout

    def constraintAxisCheckBoxes(self):
        """
        Provides a list of checkboxes with the axes for the constraints, ex:
                                                            'Translate Axis':
                                                            X[]    Y[]   Z[]

                                                            'Rotate Axis':
                                                            X[]    Y[]   Z[]
        Args: No Args.

        Return: axisWidget (QWidget); Widget with the instance of the ConstraintAxes() class.

        """
        axisWidget = PySide2.QtWidgets.QWidget()
        self.axisLayout = PySide2.QtWidgets.QVBoxLayout(axisWidget)

        self.translateAxisWidget = ConstraintAxes("Translate Axes")
        self.rotateAxisWidget = ConstraintAxes("Rotate Axes")

        self.axisLayout.addWidget(self.translateAxisWidget)
        self.axisLayout.addWidget(self.rotateAxisWidget)

        return axisWidget

    def defineAxisInUse(self):
        """
        Slot method to define the axis that will be exposed to the users.

		Returns:
			None.

        """
        currentType = self.constraintTypeCombBox.currentData()


        if maya.api.OpenMaya.MFn.kParentConstraint == currentType:
            self.translateAxisWidget.setDisabled(False)
            self.translateAxisWidget.setCheckBoxesStatus(True)

            self.rotateAxisWidget.setDisabled(False)
            self.rotateAxisWidget.setCheckBoxesStatus(True)

        elif maya.api.OpenMaya.MFn.kPointConstraint == currentType:
            self.translateAxisWidget.setDisabled(False)
            self.translateAxisWidget.setCheckBoxesStatus(True)

            self.rotateAxisWidget.setDisabled(True)
            self.rotateAxisWidget.setCheckBoxesStatus(False)

        else:
            self.translateAxisWidget.setDisabled(True)
            self.translateAxisWidget.setCheckBoxesStatus(False)

            self.rotateAxisWidget.setDisabled(False)
            self.rotateAxisWidget.setCheckBoxesStatus(True)

    @property
    def translateAxisSelected(self):
        """
        Gets the selected translate axis.

        Returns:
        	list [QWidget]: Check boxes selected.
        """
        if not self.translateAxisWidget.isEnabled():
            return None

        return self.translateAxisWidget.checkBoxesStatus

    @property
    def rotateAxisSelected(self):
        """
        Gets the selected rotate axis.

        Returns:
        	list [QWidget]: Check boxes selected.
        """
        if not self.rotateAxisWidget.isEnabled():
            return None

        return self.rotateAxisWidget.checkBoxesStatus

class ConstraintAxes(PySide2.QtWidgets.QWidget):
    """
    Provides the widget that displays the axes for the constraint.
    """
    def __init__(self, inAxisStr):

        super(ConstraintAxes, self).__init__()
        self.typeAxis = inAxisStr

        self.initMainAxesWidget()


    def initMainAxesWidget(self):
        """
        Main Initializer method for the constraintAxes, containing the checkboxes for the axes.

        Return:
            None.
        """
        mainLayout = PySide2.QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(1, 1, 250, 1)

        mainAxisLabel = PySide2.QtWidgets.QLabel(self.typeAxis)

        mainLayout.addWidget(mainAxisLabel)
        mainLayout.addLayout(self.axesCheckBoxes())


    def axesCheckBoxes(self):
        """
        Provides the checkboxes shown for the constraint.

        Returns:
            mainSubAxisLayout (QHBoxLayout): Return a single widget containing the checkboxes.
        """
        mainSubAxisLayout = PySide2.QtWidgets.QHBoxLayout()

        self.checkBoxList = []

        for axis in core.constants.BASE_TRANSFORM_AXES:
            subAxisCheckBox = PySide2.QtWidgets.QCheckBox(axis)
            subAxisCheckBox.setChecked(True)
            self.checkBoxList.append(subAxisCheckBox)
            mainSubAxisLayout.addWidget(subAxisCheckBox)

        return mainSubAxisLayout

    # --------------------------
    # ------
    # SLOTS
    # ------
    # --------------------------
    def setCheckBoxesStatus(self, inCheckBoxState=False):
        """
        Slot Method to set the

        Args:
            inCheckBoxState (bool): True sets check the boxes, False otherwise.

        Returns:
              None.
        """

        for checkBox in self.checkBoxList:
            checkBox.setChecked(inCheckBoxState)

    @property
    def checkBoxesStatus(self):
        """
        Gets the status of the checkboxes exposed to the users.

        Yield:
            str: Text of the checkbox.
        """
        for checkBox in self.checkBoxList:
            if checkBox.isChecked():
                continue
            yield checkBox.text()
