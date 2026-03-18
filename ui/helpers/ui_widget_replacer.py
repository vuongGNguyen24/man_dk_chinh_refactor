from PyQt5.QtWidgets import QWidget, QLayout


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

    visible = old.isVisible()
    enabled = old.isEnabled()
    geometry = old.geometry()

    layout = real_parent.layout()

    new_widget = new_widget_cls(*args, parent=real_parent, **kwargs)
    new_widget.setObjectName(object_name)

    if layout is not None:
        index = layout.indexOf(old)

        if index != -1:
            # ----- CASE 1: widget thuộc layout -----
            layout.removeWidget(old)
            old.deleteLater()
            layout.insertWidget(index, new_widget)

        else:
            # layout tồn tại nhưng widget không thuộc layout
            old.deleteLater()
            new_widget.setGeometry(geometry)

    else:
        # ----- CASE 2: không có layout -----
        old.deleteLater()
        new_widget.setGeometry(geometry)

    if copy_properties:
        new_widget.setVisible(visible)
        new_widget.setEnabled(enabled)

    new_widget.raise_()
    new_widget.show()
    return new_widget
