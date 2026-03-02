SET flie_in="C:/Users/Admin/Desktop/projects/wm18/man_dk_chinh_refactor/ui/views/system_diagram/layout/ban_dieu_khien_tu_xa.ui"
SET flie_out="ban_dieu_khien_tu_xa_fixed.ui"
python normalize_connection.py -i %flie_in% -o %flie_out%
python snap_conn_intersection.py -i %flie_out% -o %flie_out% -t 10
python snap_conn_with_node.py -i %flie_out% -o %flie_out% -t 10
