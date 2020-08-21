import PySide2.QtWidgets
import PySide2.QtGui
import PySide2.QtCore

class PoseSelector(PySide2.QtWidgets.QWidget):
    """
    Class that provides a widget to load and select the prop pose, reading from animan.

    """
    def __init__(self):
        super(PoseSelector, self).__init__()

        self.resize(500, 200)

        self.initPoseSelector()


    def initPoseSelector(self):
        """
        Main Initializer method for the widget, where all the widgets are called to build
        the widget.
        """

        # Widget's main layout
        mainLayout = PySide2.QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        qGroupBox = PySide2.QtWidgets.QGroupBox()
        qGroupBox.setTitle('Select the pose: ')

        groupBoxLayout = PySide2.QtWidgets.QVBoxLayout()
        qGroupBox.setLayout(groupBoxLayout)
        self.listWidget = PoseListWidget()

        groupBoxLayout.addWidget(self.listWidget)

        mainLayout.addWidget(qGroupBox)



class PoseListWidget(PySide2.QtWidgets.QListWidget):
    def __init__(self):
        super(PoseListWidget, self).__init__()


    def getDataFromItemSelected(self):
        """
        Retrieves the information of the selected items.

        Yield:
            list: Poses with its path where the data.pose file can be found.

        """
        for itemSelected in self.selectedItems():
            yield itemSelected.data(PySide2.QtCore.Qt.UserRole)
