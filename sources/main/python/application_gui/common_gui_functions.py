import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

##-\-\-\-\-\-\-\-\-\-\-\
## CALL WINDOW FUNCTIONS
##-/-/-/-/-/-/-/-/-/-/-/

# -------------------------------------
# Check if the window is already opened
def _is_window_open(parent, window_tag):

    # Initialise if it does not exist
    if window_tag not in parent.subWindows.keys():
        parent.subWindows[window_tag] = None

    return parent.subWindows[window_tag] is None

# ---------------
# Open the window
def _open_window(parent, window_class, window_tag, **kwargs):

    # Check if the window is not open yet
    if _is_window_open(parent, window_tag):
        parent.subWindows[window_tag] = window_class(parent, **kwargs)

##-\-\-\
## ALERTS
##-/-/-/

# ----------------------------
# Generic two choices messages
def choice2Message(title, text, choice1, choice2='Cancel', icon=qtw.QMessageBox.Warning):

    msg = qtw.QMessageBox()
    msg.setIcon(icon)
    msg.setText(title)
    msg.setInformativeText(text)
    msg.setWindowTitle("WARNING")
    msg.addButton(qtw.QPushButton(choice1), qtw.QMessageBox.ActionRole)
    msg.addButton(qtw.QPushButton(choice2), qtw.QMessageBox.RejectRole)
    returnValue = msg.exec_()

    if returnValue == qtw.QMessageBox.RejectRole:
        return False
    else:
        return True

# ---------------------------------------------------
# Generic error message - for errors only called once
def warningMessage(title, text, add_ok=True):

    msg = qtw.QMessageBox()
    msg.setIcon(qtw.QMessageBox.Warning)
    msg.setText(title)
    msg.setInformativeText(text)
    msg.setWindowTitle("WARNING")
    if add_ok:
        msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
    else:
        msg.setStandardButtons( qtw.QMessageBox.Cancel)
    returnValue = msg.exec_()

    if returnValue == qtw.QMessageBox.Cancel:
        return False
    else:
        return True

# ------------------------
# Display an error message
def errorMessage(title, text):

    msg = qtw.QMessageBox()
    msg.setIcon(qtw.QMessageBox.Critical)
    msg.setText(title)
    msg.setInformativeText(text)
    msg.setWindowTitle("WARNING")
    msg.setStandardButtons(qtw.QMessageBox.Ok)
    returnValue = msg.exec_()

##-\-\-\-\-\-\-\
## COMMON WIDGETS
##-/-/-/-/-/-/-/

# ---------------------
# Generate label widget
def CLabel(text):

    widgetName = qtw.QLabel(text)
    widgetNameFont = qtg.QFont()
    widgetNameFont.setBold(True)
    widgetName.setFont(widgetNameFont)

    return widgetName

# ----------------------------------------------------
# Generate a QLineEdit widget with a label on the side
def CLabelledLineEdit(label, left_side=True):

    # User name entry
    fullWidget = qtw.QWidget()
    fullLayout = qtw.QHBoxLayout( fullWidget )

    # Add the label on the left
    if left_side:
        widgetLabel = CLabel(label)
        fullLayout.addWidget(widgetLabel)

    # Add the QLineEdit widget
    lineEditWidget = qtw.QLineEdit()
    fullLayout.addWidget(lineEditWidget)

    # Add the label on the right
    if not left_side:
        widgetLabel = CLabel(label)
        fullLayout.addWidget(widgetLabel)

    fullWidget.setLayout(fullLayout)
    fullWidget.setContentsMargins(0, 0, 0, 0)
    return fullWidget, lineEditWidget

# ---------------------------
# Define the separator widget
def CHorizontalSeparator():
    separator = qtw.QFrame()
    separator.setFrameShape(qtw.QFrame.HLine)
    separator.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum)
    separator.setLineWidth(1)

    return separator

# ---------------------------
# Define the separator widget
def CVerticalSeparator():
    separator = qtw.QFrame()
    separator.setFrameShape(qtw.QFrame.VLine)
    separator.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Expanding)
    separator.setLineWidth(1)

    return separator

##-\-\-\-\-\-\-\-\-\-\-\
## EDIT WIDGET PROPERTIES
##-/-/-/-/-/-/-/-/-/-/-/

# -------------------------------------------------------
# Update the value of a spin box without releasing signal
def updateSpinBox(widget, new_value):

    # Block the signals
    widget.blockSignals(True)

    # Edit the values
    widget.setValue(new_value)

    # Release the signals
    widget.blockSignals(False)
