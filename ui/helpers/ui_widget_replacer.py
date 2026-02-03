from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect


def replace_ui_widget(
    parent: QWidget,
    object_name: str,
    new_widget_cls,
    *args,
    copy_properties: bool = True,
    **kwargs
):
    old = parent.findChild(QWidget, object_name)
    if old is None:
        raise RuntimeError(f"UI placeholder '{object_name}' not found")

    real_parent = old.parentWidget()

    geometry = old.geometry()
    visible = old.isVisible()
    enabled = old.isEnabled()

    new_widget = new_widget_cls(*args, parent=real_parent, **kwargs)

    if copy_properties:
        new_widget.setGeometry(QRect(geometry))
        new_widget.setVisible(visible)
        new_widget.setEnabled(enabled)

    new_widget.setObjectName(object_name)

    old.deleteLater()

    new_widget.raise_()
    new_widget.show()

    return new_widget
