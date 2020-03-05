
from mgear.vendor.Qt import QtWidgets
from mgear.core import pyqt


def create_button(size=17,
                  text=None,
                  icon=None,
                  toggle_icon=None,
                  icon_size=None,
                  toolTip=None):
    """Create and configure a QPsuhButton

    Args:
        size (int, optional): Size of the button
        text (str, optional): Text of the button
        icon (str, optional): Icon name
        toggle_icon (str, optional): Toggle icon name. If exist will make
                                     the button checkable
        icon_size (int, optional): Icon size
        toolTip (str, optional): Buttom tool tip

    Returns:
        QPushButton: The reated button
    """
    button = QtWidgets.QPushButton()
    button.setMaximumHeight(size)
    button.setMinimumHeight(size)
    button.setMaximumWidth(size)
    button.setMinimumWidth(size)

    if toolTip:
        button.setToolTip(toolTip)

    if text:
        button.setText(text)

    if icon:
        if not icon_size:
            icon_size = size - 3
        button.setIcon(pyqt.get_icon(icon, icon_size))

    if toggle_icon:

        button.setCheckable(True)

        def changeIcon(button=button,
                       icon=icon,
                       toggle_icon=toggle_icon,
                       size=icon_size):
            if button.isChecked():
                button.setIcon(pyqt.get_icon(toggle_icon, size))
            else:
                button.setIcon(pyqt.get_icon(icon, size))

        button.clicked.connect(changeIcon)

    return button