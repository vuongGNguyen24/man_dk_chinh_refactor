import sys
import os
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics, QPixmap

# Import from data_management module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_management import module_manager


def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file resource."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), relative_path)


class InfoPanelRenderer:
    """Handles rendering of the info panel overlay."""

    def __init__(self):
        self.scroll_offset = 0
        self.max_scroll = 0
        self.module_height = 80
        self.parameter_boxes = []  # Store parameter box regions

    def draw_info_panel(self, painter, widget_rect, selected_node_data, info_panel_rect, close_button_rect, scroll_offset):
        """Vẽ panel thông tin node overlay với layout mới."""
        if not selected_node_data:
            return

        self.scroll_offset = scroll_offset

        # Vẽ overlay tối (làm mờ background)
        overlay_color = QColor(0, 0, 0, 120)
        painter.fillRect(widget_rect, overlay_color)

        # Vẽ panel chính với nền đen
        panel_color = QColor(30, 30, 30, 255)    # Nền đen
        border_color = QColor(255, 255, 255)     # Viền trắng

        # Pen cho panel chính: viền đậm hơn nhưng dashed với khoảng cách giãn
        painter.setPen(QPen(border_color, 3))
        painter.setBrush(QBrush(panel_color))
        painter.drawRect(info_panel_rect)

        # Vẽ header với tiêu đề và nút đóng
        self._draw_panel_header(painter, selected_node_data, info_panel_rect, close_button_rect)

        # Vẽ sidebar bên trái
        self._draw_left_sidebar(painter, selected_node_data, info_panel_rect)

        # Vẽ main content area (charts)
        max_scroll = self._draw_main_content_area(painter, selected_node_data, info_panel_rect)

        return max_scroll

    def _draw_panel_header(self, painter, selected_node_data, info_panel_rect, close_button_rect):
        """Vẽ header với tiêu đề và nút X."""
        # Tiêu đề
        title_font = QFont("Arial", 14, QFont.Normal)
        painter.setFont(title_font)
        painter.setPen(QPen(QColor(255, 255, 255)))

        # Lấy tên node và loại bỏ ký tự xuống dòng
        title_text = selected_node_data.name.replace('\n', ' ')

        # Tính toán vùng hiển thị tiêu đề (tận dụng hết không gian trừ nút X)
        header_rect = QRect(info_panel_rect.left() + 20,
                           info_panel_rect.top() + 15,
                           info_panel_rect.width() - 70, 30)

        # Vẽ text trên một dòng, không word wrap
        painter.drawText(header_rect, Qt.AlignLeft | Qt.AlignVCenter, title_text)

        # Nút đóng X
        self._draw_close_button(painter, close_button_rect)

    def _draw_left_sidebar(self, painter, selected_node_data, info_panel_rect):
        """Vẽ sidebar bên trái với ô trạng thái và hình ảnh."""
        sidebar_x = info_panel_rect.left() + 20
        sidebar_y = info_panel_rect.top() + 60
        sidebar_width = 250

        # Ô trạng thái (thay vì nút "Lỗi")
        status_rect = QRect(sidebar_x, sidebar_y, sidebar_width - 20, 35)

        if selected_node_data.has_error:
            status_color = QColor(220, 60, 60)  # Màu đỏ cho lỗi
            status_text = "LỖI"
            text_color = QColor(255, 255, 255)
        else:
            status_color = QColor(60, 180, 60)  # Màu xanh cho bình thường
            status_text = "BÌNH THƯỜNG"
            text_color = QColor(255, 255, 255)

        painter.setPen(QPen(QColor(40, 40, 40), 2))
        painter.setBrush(QBrush(status_color))
        painter.drawRect(status_rect)

        painter.setFont(QFont("Arial", 10, QFont.Normal))
        painter.setPen(QPen(text_color))
        painter.drawText(status_rect, Qt.AlignCenter, status_text)

        # Hình ảnh thiết bị (thu gọn chiều cao để có chỗ cho error box)
        image_rect = QRect(sidebar_x, sidebar_y + 50, sidebar_width - 20, 150)
        self._draw_device_image(painter, image_rect, selected_node_data)

        # Ô thông tin lỗi (kéo dài đến cuối panel với padding phù hợp)
        error_box_y = sidebar_y + 50 + 150 + 10   # image_y + image_height + gap
        error_box_height = info_panel_rect.bottom() - error_box_y - 20  # Padding 20px từ đáy
        error_box_rect = QRect(sidebar_x, error_box_y, sidebar_width - 20, error_box_height)
        self._draw_error_info_box(painter, error_box_rect, selected_node_data)

    def _draw_device_image(self, painter, rect, selected_node_data):
        """Vẽ hình ảnh thiết bị từ assets."""
        # Tạo mapping từ node_id sang file ảnh
        image_mapping = {
            'bang_dien_chinh': 'bangdienchinh.png',
            'ban_dieu_khien_chinh': 'bandieukhienchinhtuxa.png',
            'ban_dieu_khien_1': 'bangdieukhientaicho1.png',
            'ban_dieu_khien_2': 'bangdieukhientaicho2.png',
            'dan_dong_huong_1': 'hopdandongkenhhuong.png',
            'dan_dong_huong_2': 'hopdandongkenhhuong.png',
            'dan_dong_tam_1': 'hopdandongkenhtam.png',
            'dan_dong_tam_2': 'hopdandongkenhtam.png',
            'hn11': 'hophn11.png',
            'hn12': 'hophn12.png',
            'hn21': 'hophn11.png',  # Dùng chung ảnh
            'hn22': 'hophn12.png',  # Dùng chung ảnh
            'giao_tiep_hang_hai': 'hopketnoihanghaivagiamsat.png',
            'ac_quy_1': 'tuacquy.png',
            'ac_quy_2': 'tuacquy.png',
            'bien_ap_1': 'tubienap.png',
            'bien_ap_2': 'tubienap.png',
            'phan_phoi_1': 'tubiendoiphanphoi.png',
            'phan_phoi_2': 'tubiendoiphanphoi.png',
            'dieu_khien_1': 'tudieukhientaicho.png',
            'dieu_khien_2': 'tudieukhientaicho.png',
            'hop_dien': 'hopdien.png',
            'hop_quang_dien_tu': 'hopquangdientu.png',
        }

        # Lấy file ảnh tương ứng với node
        image_file = image_mapping.get(selected_node_data.node_id, 'bangdienchinh.png')
        image_path = resource_path(f'assets/image/{image_file}')

        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale ảnh cho vừa với rect
                scaled_pixmap = pixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Căn giữa ảnh trong rect
                x_offset = (rect.width() - scaled_pixmap.width()) // 2
                y_offset = (rect.height() - scaled_pixmap.height()) // 2

                draw_rect = QRect(rect.x() + x_offset, rect.y() + y_offset,
                                scaled_pixmap.width(), scaled_pixmap.height())

                painter.drawPixmap(draw_rect, scaled_pixmap)
            else:
                # Fallback: vẽ placeholder nếu không load được ảnh
                painter.setPen(QPen(QColor(150, 150, 150), 1))
                painter.setBrush(QBrush(QColor(220, 220, 220)))
                painter.drawRect(rect)

                painter.setPen(QPen(QColor(100, 100, 100)))
                painter.setFont(QFont("Arial", 10))
                painter.drawText(rect, Qt.AlignCenter, "Không có\nhình ảnh")

        except Exception as e:
            # Fallback nếu có lỗi
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.setBrush(QBrush(QColor(220, 220, 220)))
            painter.drawRect(rect)

            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(rect, Qt.AlignCenter, f"Lỗi load ảnh\n{image_file}")

    def _draw_main_content_area(self, painter, selected_node_data, info_panel_rect):
        """Vẽ vùng nội dung chính với scrollable modules."""
        # Clear parameter boxes for new render
        self.parameter_boxes = []

        content_x = info_panel_rect.left() + 290
        content_y = info_panel_rect.top() + 60
        content_width = info_panel_rect.width() - 330
        content_height = info_panel_rect.height() - 100

        # Tạo clipping rect để chỉ vẽ trong vùng content
        content_rect = QRect(content_x, content_y, content_width, content_height)
        painter.setClipping(True)
        painter.setClipRect(content_rect)

        # Lấy dữ liệu module thực từ module_manager
        node_modules = module_manager.get_node_modules(selected_node_data.node_id)
        modules_list = list(node_modules.values())
        num_modules = len(modules_list)

        # Kích thước module
        module_width = content_width - 60  # Trừ thêm cho scrollbar
        self.module_height = 80
        module_spacing = 15

        # Tính toán scroll
        total_height = num_modules * (self.module_height + module_spacing) - module_spacing
        visible_height = content_height
        self.max_scroll = max(0, total_height - visible_height)

        # Vẽ các module với offset scroll - dịch xuống 10px để tránh cắt chữ
        current_y = content_y - self.scroll_offset + 10

        for i, module_data in enumerate(modules_list):
            module_rect = QRect(content_x + 20, current_y, module_width, self.module_height)

            # Chỉ vẽ module nếu nó nằm trong vùng hiển thị
            if (current_y + self.module_height >= content_y and
                current_y <= content_y + content_height):
                self._draw_module(painter, module_rect, module_data, selected_node_data.node_id)

            current_y += self.module_height + module_spacing

        # Vẽ scroll bar nếu cần
        if self.max_scroll > 0:
            self._draw_scrollbar(painter, content_rect)

        # Tắt clipping
        painter.setClipping(False)

        return self.max_scroll

    def _draw_scrollbar(self, painter, content_rect):
        """Vẽ thanh scroll."""
        scrollbar_width = 8
        scrollbar_x = content_rect.right() - scrollbar_width - 5
        scrollbar_y = content_rect.top() + 5
        scrollbar_height = content_rect.height() - 10

        # Nền scrollbar
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        scrollbar_bg_rect = QRect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        painter.drawRect(scrollbar_bg_rect)

        # Thumb scrollbar
        if self.max_scroll > 0:
            total_content_height = self.max_scroll + content_rect.height()
            thumb_height = max(20, int(scrollbar_height * content_rect.height() / total_content_height))
            thumb_y = scrollbar_y + int(self.scroll_offset * (scrollbar_height - thumb_height) / self.max_scroll)

            painter.setBrush(QBrush(QColor(150, 150, 150)))
            thumb_rect = QRect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            painter.drawRect(thumb_rect)

    def _draw_module(self, painter, rect, module_data, node_id=''):
        """Vẽ một module với 4 thông số sử dụng dữ liệu thực."""
        # Tính toán vị trí
        param_width = (rect.width() - 40) // 4
        param_height = 50
        param_y = rect.top() + 25

        # Tạo rect cho module với cạnh dưới đi qua trung điểm của parameter boxes
        module_bottom = param_y + param_height // 2
        module_rect = QRect(rect.left(), rect.top(), rect.width(), module_bottom - rect.top())

        # Màu sắc khung module theo trạng thái
        border_color = QColor(150, 150, 150)  # Xám cho bình thường

        # Vẽ khung module với cạnh dưới đi qua trung điểm các box
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(module_rect)

        # Vẽ tiêu đề module với background để che đường kẻ
        title_text = module_data.name
        id_text = module_data.config_id if hasattr(module_data, 'config_id') and module_data.config_id else ""

        # Set font và tính toán kích thước text cho tên module (bên trái)
        painter.setFont(QFont("Arial", 10, QFont.Normal))
        font_metrics = QFontMetrics(painter.font())
        text_width = font_metrics.horizontalAdvance(title_text)
        text_height = font_metrics.height()

        # Tạo background rect cho text tên module (padding đủ lớn để không che dấu)
        title_bg_rect = QRect(rect.left() + 8, rect.top() - 10, text_width + 14, text_height + 8)

        # Vẽ background che đường kẻ (cùng màu với background panel)
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(QColor(30, 30, 30)))  # Màu nền panel
        painter.drawRect(title_bg_rect)

        # Vẽ text tiêu đề (bên trái) - đủ khoảng trống phía trên cho dấu
        painter.setPen(QPen(QColor(255, 255, 255)))
        title_rect = QRect(rect.left() + 12, rect.top() - 8, text_width, text_height + 4)
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignTop, title_text)

        # Vẽ ID bên phải (nếu có)
        if id_text:
            id_width = font_metrics.horizontalAdvance(id_text)
            
            # Tạo background rect cho ID
            id_bg_rect = QRect(rect.right() - id_width - 28, rect.top() - 8, id_width + 10, text_height + 4)
            
            # Vẽ background cho ID
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(QColor(30, 30, 30)))
            painter.drawRect(id_bg_rect)
            
            # Vẽ text ID (màu xanh nhạt để phân biệt)
            painter.setPen(QPen(QColor(100, 200, 255)))
            painter.setFont(QFont("Arial", 9, QFont.Normal))
            id_rect = QRect(rect.right() - id_width - 23, rect.top() - 6, id_width, 20)
            painter.drawText(id_rect, Qt.AlignRight | Qt.AlignVCenter, id_text)

        # Lấy thông số thực từ module_data
        params = module_data.parameters
        voltage_display = f"{params.voltage:.1f}"
        current_display = f"{params.current:.1f}"
        power_display = f"{params.power:.1f}"
        temperature_display = f"{params.temperature:.1f}"

        # Vị trí các thông số (4 cột) - cạnh dưới module đi qua trung điểm các box này
        parameters = [
            ("Điện áp", f"{voltage_display}V"),
            ("Dòng điện", f"{current_display}A"),
            ("Công suất", f"{power_display}W"),
            ("Nhiệt độ", f"{temperature_display}°C")
        ]

        for i, (label, value) in enumerate(parameters):
            param_x = rect.left() + 20 + i * param_width
            param_rect = QRect(param_x, param_y, param_width - 10, param_height)

            # Store parameter box for click detection
            self.parameter_boxes.append({
                'rect': param_rect,
                'parameter_name': label,
                'module_name': module_data.name,
                'node_id': node_id
            })

            self._draw_parameter_box(painter, param_rect, label, value, module_data.name)

    def _draw_parameter_box(self, painter, rect, label, value, module_name="Module 1"):
        """Vẽ một hộp thông số với đường kẻ màu theo trạng thái."""
        # Nền thông số (màu xám đậm như trong hình)
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(70, 70, 70)))
        painter.drawRect(rect)

        # Label (phần trên) - căn giữa theo chiều cao mới
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.setFont(QFont("Arial", 9))
        label_height = rect.height() // 4  # Nửa trên của box
        label_rect = QRect(rect.left(), rect.top() + 5, rect.width(), label_height)
        painter.drawText(label_rect, Qt.AlignCenter, label)

        # Xác định màu đường kẻ dựa trên giá trị và loại thông số
        line_color = self._get_parameter_status_color(label, value, module_name)

        # Đường phân cách với màu theo trạng thái - ở giữa box
        painter.setPen(QPen(line_color, 2))
        separator_y = rect.top() + rect.height() // 2
        painter.drawLine(rect.left() + 5, separator_y, rect.right() - 5, separator_y)

        # Giá trị (phần dưới) - căn giữa theo chiều cao mới
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 12, QFont.Normal))
        value_height = rect.height() // 2 - 2  # Nửa dưới của box
        value_rect = QRect(rect.left(), separator_y + 2, rect.width(), value_height)
        painter.drawText(value_rect, Qt.AlignCenter, value)

    def _get_parameter_status_color(self, label, value, module_name="Module 1"):
        """Xác định màu sắc dựa trên trạng thái thông số."""
        # Import unified threshold manager
        try:
            from data_management.unified_threshold_manager import get_threshold_for_parameter, is_parameter_normal
        except ImportError:
            # Fallback nếu không import được
            return QColor(0, 255, 0)

        # Lấy giá trị số từ string (bỏ đơn vị)
        try:
            # Lấy tất cả ký tự số và dấu chấm thập phân
            numeric_str = ''.join(c for c in value if c.isdigit() or c == '.')
            numeric_value = float(numeric_str)
        except:
            return QColor(0, 255, 0)  # Xanh mặc định nếu không parse được

        # Kiểm tra trạng thái dựa trên file cấu hình
        if is_parameter_normal(module_name, label, numeric_value):
            return QColor(0, 255, 0)    # Xanh - bình thường
        else:
            return QColor(255, 0, 0)    # Đỏ - cao/thấp

    def _draw_close_button(self, painter, close_button_rect):
        """Vẽ nút đóng X."""
        # Nền nút đóng (trong suốt)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(close_button_rect)

        # Vẽ chữ X
        painter.setPen(QPen(QColor(255, 255, 255), 3))  # X màu trắng
        margin = 8
        x1 = close_button_rect.left() + margin
        y1 = close_button_rect.top() + margin
        x2 = close_button_rect.right() - margin
        y2 = close_button_rect.bottom() - margin

        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y1, x1, y2)

    def _draw_error_info_box(self, painter, rect, selected_node_data):
        """Vẽ ô thông tin lỗi dưới hình ảnh node."""
        # Nền ô thông tin lỗi
        if selected_node_data.has_error:
            # Nền đỏ nhạt khi có lỗi
            bg_color = QColor(80, 30, 30)  # Đỏ đậm
            border_color = QColor(220, 60, 60)  # Đỏ sáng
            text_color = QColor(255, 255, 255)  # Trắng
        else:
            # Nền xanh nhạt khi bình thường
            bg_color = QColor(30, 60, 30)  # Xanh đậm
            border_color = QColor(60, 180, 60)  # Xanh sáng
            text_color = QColor(255, 255, 255)  # Trắng

        # Vẽ nền và viền
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(bg_color))
        painter.drawRect(rect)

        # Tiêu đề
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.setPen(QPen(text_color))
        title_rect = QRect(rect.left() + 10, rect.top() + 10, rect.width() - 20, 25)

        if selected_node_data.has_error:
            painter.drawText(title_rect, Qt.AlignCenter, "THÔNG TIN LỖI")
        else:
            painter.drawText(title_rect, Qt.AlignCenter, "TRẠNG THÁI BÌNH THƯỜNG")

        # Nội dung lỗi
        content_rect = QRect(rect.left() + 10, rect.top() + 40, rect.width() - 20, rect.height() - 50)
        painter.setFont(QFont("Arial", 10))

        if selected_node_data.has_error:
            # Lấy danh sách lỗi từ modules
            error_messages = self._get_node_error_messages(selected_node_data)

            if error_messages:
                # Hiển thị tất cả lỗi
                error_text = "\n".join([f"• {msg}" for msg in error_messages])
                painter.drawText(content_rect, Qt.AlignTop | Qt.TextWordWrap, error_text)
            else:
                painter.drawText(content_rect, Qt.AlignTop, "• Lỗi hệ thống chung")
        else:
            painter.drawText(content_rect, Qt.AlignTop | Qt.TextWordWrap, "• Tất cả module hoạt động bình thường\n• Không phát hiện lỗi")

    def _get_node_error_messages(self, selected_node_data):
        """Lấy danh sách thông báo lỗi từ tất cả modules của node."""
        error_messages = []

        try:
            # Import module manager - improved import handling
            from data_management.module_data_manager import module_manager

            # Lấy modules của node
            node_modules = module_manager.get_node_modules(selected_node_data.node_id)

            for module in node_modules.values():
                if module.status == "error" and module.error_messages:
                    for error_msg in module.error_messages:
                        # Format: "Module X: error message"
                        formatted_msg = f"{module.name}: {error_msg}"
                        error_messages.append(formatted_msg)

            # Thêm lỗi node riêng nếu có
            if hasattr(selected_node_data, 'error_messages') and selected_node_data.error_messages:
                for error_msg in selected_node_data.error_messages:
                    error_messages.append(f"Node: {error_msg}")

        except Exception as e:
            # Fallback nếu không thể lấy thông tin module
            error_messages = ["Không thể lấy thông tin lỗi chi tiết"]

        return error_messages

    def get_parameter_boxes(self):
        """Return the list of parameter boxes for click detection."""
        return self.parameter_boxes