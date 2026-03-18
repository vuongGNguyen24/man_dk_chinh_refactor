from typing import List, Union
from PyQt5.QtWidgets import QApplication
import yaml

def load_app_qss(app: QApplication, paths: List[str]):
    """Load qss files cho Qt application.
    
    
    File sau sẽ override style của các file đã load trước!
    
    Args:
        app (QApplication): application object cần load style
        paths (List[str]): danh sách đường đẫn các file .qss, theo thứ tự load style.
    """
    styles = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            styles.append(f.read())
    app.setStyleSheet("\n".join(styles))

def load_styles_from_yaml(app: QApplication, file_name: str, sections: Union[str, List[str], None]=None, base_path: str=None):
    """Load qss files cho Qt application.
    
    File sau sẽ override style của các file đã load trước!
    
    Args:
        app (QApplication): application object cần load style
        path (str): path của file .yaml
        sections (Union[str, List[str], None]): sections cần load theo thứ tự, default là tất cả sections theo thứ tự trong file .yaml
    """
    import os
    with open(os.path.join(base_path, file_name), "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    if isinstance(sections, str):
        sections = [sections]
    elif sections is None:
        sections = manifest.keys()
    
    all_qss_paths = []
    for section in sections:
        all_qss_paths.extend(manifest[section])
        
    if base_path:
        all_qss_paths = [os.path.join(base_path, path) for path in all_qss_paths]
    load_app_qss(app, all_qss_paths)


def repolish(widget):
    """Cập nhật style cho qt element sau khi setProperty.
    
    Args:
        widget (QWidget): widget cần update style
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
    
def set_multiple_property(widget, **kwargs):
    """Cập nhật style cho qt element sau khi setProperty.
    
    Args:
        widget (QWidget): widget cần update style
        kwargs (Dict[str, str]): property name and value
    
    Example:
        set_multiple_property(widget, role="angle-input", variant="overlay")
    """
    for key, value in kwargs.items():
        widget.setProperty(key, value)
    repolish(widget)