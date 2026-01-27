# -*- coding: utf-8 -*-

import os
import sys
import yaml
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor, QRadialGradient, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice, QSize, pyqtProperty, QPointF, QRectF
from PyQt5 import QtCore, QtWidgets
from xml.etree import ElementTree as ET

# Refactored: Use common utilities instead of duplicated functions
try:
    from common.utils import resource_path, load_button_colors
    from common.constants import Colors, SystemLimits

    BUTTON_COLORS = load_button_colors()

    def reload_button_colors():
        """Reload button colors from config.yaml"""
        global BUTTON_COLORS
        BUTTON_COLORS = load_button_colors()
        return BUTTON_COLORS

except ImportError:
    # Fallback to legacy implementation if common module not available
    print("Warning: Common utilities not found. Using legacy implementation.")

    def load_button_colors():
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.yaml')
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('ButtonColors', {})
        except Exception:
            return {}

    def resource_path(relative_path):
        """Lấy absolute path của resource."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    BUTTON_COLORS = load_button_colors()

    def reload_button_colors():
        """Reload button colors from config.yaml"""
        global BUTTON_COLORS
        BUTTON_COLORS = load_button_colors()
        return BUTTON_COLORS

class SVGColorChanger:
    """Class để thay đổi màu sắc của SVG files programmatically."""
    
    @staticmethod
    def create_colored_icon(svg_path, color="#ffffff", size=(48, 48), alpha=255):
        """
        Tạo QIcon từ SVG file với màu sắc tùy chỉnh.
        
        Args:
            svg_path (str): Đường dẫn đến file SVG
            color (str): Màu sắc hex (ví dụ: "#ffffff" cho màu trắng)
            size (tuple): Kích thước icon (width, height)
            alpha (int): Độ trong suốt 0-255
            
        Returns:
            QIcon: Icon với màu đã được thay đổi
        """
        try:
            # Đọc file SVG
            full_path = resource_path(svg_path)
            if not os.path.exists(full_path):
                print(f"Error: SVG file not found: {full_path}")
                return QIcon()
                
            with open(full_path, 'r', encoding='utf-8') as file:
                svg_content = file.read()
            
            # Thay đổi màu sắc trong SVG content
            modified_svg = SVGColorChanger._change_svg_colors(svg_content, color)
            
            # Tạo QIcon từ SVG đã chỉnh sửa, áp dụng alpha nếu cần
            return SVGColorChanger._create_icon_from_svg_string(modified_svg, size, alpha)
            
        except Exception as e:
            print(f"Error creating colored icon: {e}")
            return QIcon()
    
    @staticmethod
    def _change_svg_colors(svg_content, target_color):
        # Nếu target_color là #ffffffff (8 ký tự), chuyển thành #ffffff (6 ký tự)
        if isinstance(target_color, str) and target_color.startswith('#') and len(target_color) == 9:
            # Chỉ lấy 6 ký tự đầu (bỏ alpha)
            target_color = target_color[:7]
        """
        Thay đổi tất cả màu sắc trong SVG content.
        
        Args:
            svg_content (str): Nội dung SVG
            target_color (str): Màu sắc mục tiêu
            
        Returns:
            str: SVG content đã được chỉnh sửa
        """
        try:
            # Parse SVG XML
            root = ET.fromstring(svg_content)
            
            # Định nghĩa namespace cho SVG
            namespace = {'svg': 'http://www.w3.org/2000/svg'}
            
            # Tìm và thay đổi tất cả các thuộc tính màu sắc
            for elem in root.iter():
                # Thay đổi fill attribute
                if 'fill' in elem.attrib:
                    if elem.attrib['fill'].lower() not in ['none', 'transparent']:
                        elem.attrib['fill'] = target_color
                
                # Thay đổi stroke attribute
                if 'stroke' in elem.attrib:
                    if elem.attrib['stroke'].lower() not in ['none', 'transparent']:
                        elem.attrib['stroke'] = target_color
                
                # Thay đổi style attribute nếu có
                if 'style' in elem.attrib:
                    style = elem.attrib['style']
                    # Thay đổi fill trong style
                    import re
                    style = re.sub(r'fill:\s*#[0-9a-fA-F]{3,6}', f'fill:{target_color}', style)
                    style = re.sub(r'fill:\s*rgb\([^)]+\)', f'fill:{target_color}', style)
                    style = re.sub(r'stroke:\s*#[0-9a-fA-F]{3,6}', f'stroke:{target_color}', style)
                    style = re.sub(r'stroke:\s*rgb\([^)]+\)', f'stroke:{target_color}', style)
                    elem.attrib['style'] = style
            
            # Chuyển đổi lại thành string
            return ET.tostring(root, encoding='unicode')
            
        except Exception as e:
            print(f"Error changing SVG colors: {e}")
            return svg_content
    
    @staticmethod
    def _create_icon_from_svg_string(svg_string, size, alpha=255):
        """
        Tạo QIcon từ SVG string.
        
        Args:
            svg_string (str): Nội dung SVG
            size (tuple): Kích thước icon
            alpha (int): Độ trong suốt 0-255
            
        Returns:
            QIcon: Icon được tạo từ SVG
        """
        try:
            # Basic validation of requested size
            if not size or len(size) < 2:
                return QIcon()
            width = int(size[0]) if size[0] is not None else 0
            height = int(size[1]) if size[1] is not None else 0
            if width <= 0 or height <= 0:
                # Avoid creating zero-sized QPixmaps which have no paint engine
                return QIcon()

            # Chuyển SVG string thành QByteArray
            svg_bytes = QByteArray(svg_string.encode('utf-8'))

            # Tạo QSvgRenderer từ QByteArray
            renderer = QSvgRenderer(svg_bytes)
            if not renderer.isValid():
                return QIcon()

            # Tạo QPixmap với kích thước mong muốn (guaranteed > 0)
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.transparent)

            # Vẽ SVG lên QPixmap using safe QPainter lifecycle
            painter = QPainter()
            began = painter.begin(pixmap)
            if not began:
                # Painter failed to begin on this device
                return QIcon()
            try:
                painter.setRenderHint(QPainter.Antialiasing)
                renderer.render(painter)
            finally:
                if painter.isActive():
                    painter.end()

            # Áp dụng alpha nếu cần
            if alpha < 255:
                alpha_pixmap = QPixmap(pixmap.size())
                if not alpha_pixmap.isNull():
                    alpha_pixmap.fill(Qt.transparent)
                    painter = QPainter()
                    began = painter.begin(alpha_pixmap)
                    if began:
                        try:
                            painter.setOpacity(alpha / 255.0)
                            painter.drawPixmap(0, 0, pixmap)
                        finally:
                            if painter.isActive():
                                painter.end()
                        pixmap = alpha_pixmap

            # Tạo QIcon từ QPixmap
            return QIcon(pixmap)

        except Exception as e:
            # Keep this lightweight: avoid spamming logs in normal UI flow
            print(f"Error creating icon from SVG string: {e}")
            return QIcon()
    
    @staticmethod
    def create_colored_pixmap(svg_path, color="#ffffff", size=(48, 48), alpha=255):
        """
        Tạo QPixmap từ SVG file với màu sắc tùy chỉnh.
        
        Args:
            svg_path (str): Đường dẫn đến file SVG
            color (str): Màu sắc hex
            size (tuple): Kích thước pixmap
            alpha (int): Độ trong suốt 0-255
            
        Returns:
            QPixmap: Pixmap với màu đã được thay đổi
        """
        icon = SVGColorChanger.create_colored_icon(svg_path, color, size, alpha)
        return icon.pixmap(size[0], size[1])

class IsometricButton(QtWidgets.QPushButton):
    """Custom QPushButton với hiệu ứng isometric."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Refactored: Use constants where available
        try:
            from common.constants import Colors, ISOMETRIC_OFFSET_X, ISOMETRIC_OFFSET_Y, ISOMETRIC_BUTTON_HEIGHT, BUTTON_BORDER_RADIUS
            self.top_color = Colors.MAIN_BACKGROUND
            self.border_color = Colors.WHITE_BORDER
            self.border_radius = BUTTON_BORDER_RADIUS
            self.offset_x = ISOMETRIC_OFFSET_X
            self.offset_y = ISOMETRIC_OFFSET_Y
            self.top_surface_height = ISOMETRIC_BUTTON_HEIGHT
        except ImportError:
            # Fallback to hardcoded values
            self.top_color = "#121212"
            self.border_color = "#ffffff"
            self.border_radius = 8
            self.offset_x = 3
            self.offset_y = 6
            self.top_surface_height = 80
        
    def set_colors(self, top_color, border_color, border_radius):
        """Thiết lập màu sắc cho button."""
        self.top_color = top_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.update()  # Force repaint when colors change
    
    def set_top_surface_height(self, height):
        """Thiết lập chiều cao cố định cho mặt trên."""
        self.top_surface_height = height
        
    def paintEvent(self, event):
        """Vẽ button với hiệu ứng isometric."""
        from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
        from PyQt5.QtCore import QRect
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Lấy kích thước button
        width = self.width()
        height = self.height()
        
        # Kiểm tra trạng thái pressed
        is_pressed = self.isDown()
        
        # Tính toán offset điều chỉnh để nút có offset thấp được dịch xuống
        # Sử dụng 12 làm mốc chuẩn (offset của nút trắng)
        standard_offset = 12
        adjustment = standard_offset - self.offset_y
        
        if not is_pressed:
            # Vẽ mặt dưới (shadow) với chiều cao cố định
            shadow_color = QColor(self.top_color).darker(150)
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(QPen(QColor(self.border_color), 1))
            # Mặt dưới có cùng chiều cao với mặt trên và cách mặt trên một khoảng offset_y
            # Thêm adjustment để dịch chuyển nút đen xuống
            shadow_rect = QRect(0, self.offset_y + adjustment, width, self.top_surface_height)
            painter.drawRoundedRect(shadow_rect, self.border_radius, self.border_radius)
        
        # Vẽ mặt trên (button chính) với chiều cao cố định
        main_color = QColor(self.top_color)
        # Sử dụng chiều cao cố định cho mặt trên để đảm bảo tất cả các nút có cùng kích cỡ
        main_height = self.top_surface_height
        if is_pressed:
            main_color = main_color.darker(120)
            # Khi pressed, mặt trên xuống gần mặt dưới
            main_rect = QRect(0, self.offset_y + adjustment, width, main_height)
        else:
            # Khi không pressed, mặt trên ở đỉnh button (có thêm adjustment)
            main_rect = QRect(0, 0 + adjustment, width, main_height)
        
        # Sử dụng màu đơn giản thay vì gradient
        painter.setBrush(QBrush(main_color))
        painter.setPen(QPen(QColor(self.border_color), 1))
        painter.drawRoundedRect(main_rect, self.border_radius, self.border_radius)
        
        # Vẽ icon
        icon = self.icon()
        if not icon.isNull():
            icon_size = self.iconSize()
            icon_x = main_rect.x() + (main_rect.width() - icon_size.width()) // 2
            icon_y = main_rect.y() + (main_rect.height() - icon_size.height()) // 2
            icon_rect = QRect(icon_x, icon_y, icon_size.width(), icon_size.height())
            icon.paint(painter, icon_rect)
        
        painter.end()

class ColoredSVGButton:
    """Helper class để tạo button với SVG icon có màu tùy chỉnh và hiệu ứng isometric."""
    
    @staticmethod
    def setup_button(button, svg_path, icon_color="#ffffff", icon_size=(48, 48), 
                    top_color="#121212", border_color="#ffffff", border_radius=8, isometric=False, icon_alpha=255):
        """
        Thiết lập button với SVG icon có màu tùy chỉnh và hiệu ứng isometric.
        
        Args:
            button: QPushButton object hoặc IsometricButton object
            svg_path (str): Đường dẫn đến file SVG
            icon_color (str): Màu của icon
            icon_size (tuple): Kích thước icon
            top_color (str): Màu nền
            border_color (str): Màu viền
            border_radius (int): Bán kính viền
            isometric (bool): Có tạo hiệu ứng isometric không
            icon_alpha (int): Độ trong suốt 0-255 cho icon
        """
        try:
            # Tạo icon với màu tùy chỉnh và alpha
            colored_icon = SVGColorChanger.create_colored_icon(svg_path, icon_color, icon_size, icon_alpha)
            
            # Thiết lập icon cho button
            button.setIcon(colored_icon)
            button.setIconSize(QSize(icon_size[0], icon_size[1]))
            button.setText("")  # Remove text
            
            # Force icon update
            button.setIconSize(button.iconSize())  # Force refresh
            
            if isometric and hasattr(button, 'set_colors'):
                # Đây là IsometricButton, thiết lập màu sắc và cập nhật
                button.set_colors(top_color, border_color, border_radius)
                button.update()  # Trigger repaint with new colors
                button.repaint()  # Force immediate repaint
            else:
                # Button thông thường, thiết lập style
                if border_color == "transparent":
                    # Không có viền
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {top_color};
                            border: none;
                            border-radius: {border_radius}px;
                        }}
                        QPushButton:pressed {{
                            background-color: #333333;
                        }}
                        QPushButton:hover {{
                            background-color: #444444;
                        }}
                    """)
                else:
                    # Có viền
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {top_color};
                            border: 1px solid {border_color};
                            border-radius: {border_radius}px;
                        }}
                        QPushButton:pressed {{
                            background-color: #333333;
                        }}
                        QPushButton:hover {{
                            background-color: #444444;
                        }}
                    """)
            
        except Exception as e:
            print(f"Error setting up colored SVG button: {e}")
    
    @staticmethod
    def create_isometric_button(parent=None):
        """
        Tạo một IsometricButton mới.
        
        Args:
            parent: Widget cha
            
        Returns:
            IsometricButton: Button với hiệu ứng isometric
        """
        return IsometricButton(parent)


class BulletIsometricButton(QtWidgets.QPushButton):
    """Custom button với hiệu ứng isometric 3D được vẽ bằng QPainter cho các nút ống phóng."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.is_ready = True
        self.is_selected = False
        self.is_pressed_down = False  # Trạng thái khi đang nhấn
        self.isometric_factor = 0.7  # Hệ số co cho hiệu ứng 3D
        self._current_depth = 5  # Độ sâu hiện tại cho animation - tăng từ 3 lên 5
        
        # Cache màu sắc để tránh load config nhiều lần
        self._button_colors = None
        self._load_colors()
    
    def _load_colors(self):
        """Load màu sắc từ config"""
        self._button_colors = load_button_colors()
    
    def refresh_colors(self):
        """Refresh màu sắc từ config mới"""
        self._load_colors()
        self.update()
    
    @pyqtProperty(float)
    def current_depth(self):
        return self._current_depth
    
    @current_depth.setter
    def current_depth(self, value):
        self._current_depth = value
        self.update()  # Trigger repaint khi depth thay đổi
        
    def set_state(self, is_ready: bool, is_selected: bool):
        """Cập nhật trạng thái của button."""
        self.is_ready = is_ready
        self.is_selected = is_selected
        
        # Cập nhật current_depth dựa trên trạng thái mới
        if not self.is_ready:
            self._current_depth = 2.5  # Nút không sẵn sàng
        elif self.is_selected:
            self._current_depth = 2.5  # Nút được chọn
        else:
            self._current_depth = 5  # Nút ready và không selected
        
        self.update()
        
    def mousePressEvent(self, event):
        """Xử lý sự kiện nhấn chuột - tạo hiệu ứng thụt xuống."""
        self.is_pressed_down = True
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Xử lý sự kiện thả chuột - trở về trạng thái bình thường."""
        self.is_pressed_down = False
        self.update()
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Vẽ button với hiệu ứng isometric 3D."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Kích thước và vị trí
        rect = self.rect()
        center = QPointF(rect.width()/2, rect.height()/2)
        radius = min(rect.width(), rect.height()) / 2 - 5
        
        # Màu sắc dựa trên trạng thái - cải thiện độ tương phản

        # Lấy màu từ cached config
        if self._button_colors is None:
            self._load_colors()
            
        selected_cfg = self._button_colors.get('selected', {})
        enabled_cfg = self._button_colors.get('enabled', {})
        disabled_cfg = self._button_colors.get('disabled', {})

        if self.is_selected:
            # Sử dụng màu từ config cho selected
            border_color = selected_cfg.get('border_color', '#000000')
            top_color = QColor(selected_cfg.get('top_color', '#f8f8f8'))
        elif self.is_ready:
            # Sử dụng màu từ config cho enabled
            border_color = enabled_cfg.get('border_color', '#30ffffff')
            top_color = QColor(enabled_cfg.get('top_color', '#ffffff'))
        else:
            # Sử dụng màu từ config cho disabled
            border_color = disabled_cfg.get('border_color', '#30ffffff')
            top_color = QColor(disabled_cfg.get('top_color', '#121212'))
            
        # Vẽ đổ bóng (điều chỉnh dựa trên trạng thái nhấn hoặc selected)
        is_depressed = self.is_pressed_down or self.is_selected
        
        # Chỉ vẽ nếu nút sẵn sàng (không trong suốt)
        if self.is_ready:
            shadow_offset = 2 if is_depressed else 4
            shadow_opacity = 30 if is_depressed else 60
            shadow_rect = QRectF(center.x() - radius + shadow_offset, 
                               center.y() - radius + shadow_offset,
                               radius * 2, radius * 2)
            shadow_gradient = QRadialGradient(shadow_rect.center(), radius)
            shadow_gradient.setColorAt(0, QColor(0, 0, 0, shadow_opacity))
            shadow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(shadow_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(shadow_rect)
        
        # Sử dụng current_depth cho animation thay vì tính toán cố định
        depth_offset = self._current_depth
        
        # Chỉ vẽ các ellipse nếu nút sẵn sàng
        if self.is_ready:
            # Vẽ mặt dưới (ellipse tối hơn) - LUÔN Ở VỊ TRÍ CỐ ĐỊNH
            bottom_rect = QRectF(center.x() - radius, center.y() - radius * self.isometric_factor + 1,
                               radius * 2, radius * 2 * self.isometric_factor)
            bottom_gradient = QRadialGradient(bottom_rect.center(), radius)
            bottom_gradient.setColorAt(0, top_color.darker(150))
            bottom_gradient.setColorAt(1, top_color.darker(200))
            painter.setBrush(QBrush(bottom_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(bottom_rect)
            
            # Vẽ mặt trên (ellipse sáng hơn) với gradient cải thiện
            top_rect = QRectF(center.x() - radius, center.y() - radius * self.isometric_factor - depth_offset,
                            radius * 2, radius * 2 * self.isometric_factor)
            painter.setBrush(QBrush(top_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(top_rect)
        else:
            # Vẽ viền cho nút không sẵn sàng - tạo hiệu ứng 3D với viền
            
            # Vẽ mặt dưới (viền) - LUÔN Ở VỊ TRÍ CỐ ĐỊNH
            bottom_rect = QRectF(center.x() - radius, center.y() - radius * self.isometric_factor + 1,
                               radius * 2, radius * 2 * self.isometric_factor)
            painter.setBrush(Qt.NoBrush)  # Không fill
            painter.setPen(QPen(QColor(border_color), 1))  # Viền lấy từ config
            painter.drawEllipse(bottom_rect)
            
            # Vẽ mặt trên (fill màu từ config cho disabled)
            top_rect = QRectF(center.x() - radius, center.y() - radius * self.isometric_factor - depth_offset,
                            radius * 2, radius * 2 * self.isometric_factor)
            painter.setBrush(QBrush(top_color))  # Sử dụng top_color từ config
            painter.setPen(QPen(QColor(border_color), 1))  # Viền lấy từ config
            painter.drawEllipse(top_rect)
        
        # Vẽ text với độ tương phản cao - chỉ vẽ nếu nút sẵn sàng
        if self.is_ready:
            text_offset = 1 if is_depressed else 0
            
            # Cải thiện màu text dựa trên trạng thái
            if self.is_selected:
                painter.setPen(QPen(QColor(selected_cfg.get('text_color', '#5f5f5f')), 2))  # Màu text từ config cho selected
            else:
                painter.setPen(QPen(QColor(enabled_cfg.get('text_color', '#000000')), 2))  # Màu text từ config cho enabled
                
            font = QFont("Tahoma", 18, QFont.Bold)
            painter.setFont(font)
            text_rect = QRectF(center.x() - radius, center.y() - radius * self.isometric_factor - depth_offset + text_offset,
                             radius * 2, radius * 2 * self.isometric_factor)
            painter.drawText(text_rect, Qt.AlignCenter, self.text())
        else:
            # Vẽ text cho nút không sẵn sàng - sử dụng màu từ config
            font = QFont("Tahoma", 18, QFont.Bold)
            painter.setFont(font)
            text_rect = QRectF(center.x() - radius, center.y() - radius * self.isometric_factor - depth_offset,
                             radius * 2, radius * 2 * self.isometric_factor)
            
            # Vẽ viền cho text sử dụng border_color từ config
            painter.setPen(QPen(QColor(disabled_cfg.get('border_color', '#30ffffff')), 1))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:  # Không vẽ ở vị trí trung tâm
                        offset_rect = QRectF(text_rect.x() + dx, text_rect.y() + dy, 
                                           text_rect.width(), text_rect.height())
                        painter.drawText(offset_rect, Qt.AlignCenter, self.text())
            
            # Vẽ text chính sử dụng text_color từ config cho disabled
            painter.setPen(QPen(QColor(disabled_cfg.get('text_color', '#30ffffff')), 2))
            painter.drawText(text_rect, Qt.AlignCenter, self.text())
