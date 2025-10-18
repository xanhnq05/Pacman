# pacman/core/grid.py
import os
import sys

class Grid:
    """
    Biểu diễn mê cung (layout), chứa các thông tin tĩnh như tường, kích thước.
    Cũng xử lý các luật liên quan đến cấu trúc map như Teleport và Xoay.
    """
    def __init__(self, layout_file):
        self.layout_file = layout_file
        # self.layout_list sẽ lưu mảng 2D (list of lists) để có thể chỉnh sửa (ăn tường, xoay)
        self.layout_list = self._load_layout() 
        
        self.rows = len(self.layout_list)
        self.cols = len(self.layout_list[0])
        
        self.initial_pacman_pos = None
        self.initial_food_pos = []
        self.initial_magical_pie = []
        self.exitgate_pos = None
        self.teleport_corners = []
        self.initial_ghosts_info = []

        self._find_initial_objects()
        
        # Lưu trạng thái ban đầu để có thể reset
        self._save_initial_state()

    def _load_layout(self):
        """
        Đọc file layout và chuyển thành một mảng 2D (list of lists) để dễ dàng sửa đổi
        khi Pacman ăn tường hoặc mê cung xoay.
        """
        # Giả định layout_file nằm ở 'data/layout.txt'
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_dir, self.layout_file)
        
        try:
            with open(full_path, 'r') as f:
                return [list(line.strip()) for line in f] 
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file layout tại {full_path}")
            sys.exit()

    def _find_initial_objects(self):
        """
        Tìm và lưu trữ vị trí ban đầu của Pacman, thức ăn, cổng thoát, v.v.
        """
        self.initial_ghosts_info = []
        for r in range(self.rows):
            for c in range(self.cols):
                char = self.layout_list[r][c]
                if char == 'P':
                    self.initial_pacman_pos = (r, c) # Lưu dưới dạng tuple (bất biến)
                elif char == '.':
                    self.initial_food_pos.append((r, c))
                elif char == '0':
                    self.initial_magical_pie.append((r, c))
                elif char == 'E':
                    self.exitgate_pos = (r, c)
                elif char == 'G':
                    direction = (0, 1) # Di chuyển sang phải
                    # Gán màu khác nhau cho mỗi ma dựa trên vị trí
                    ghost_colors = ["red", "pink", "blue", "orange"]
                    color = ghost_colors[len(self.initial_ghosts_info) % len(ghost_colors)]
                    self.initial_ghosts_info.append(((r, c), color, direction))
        
        # Xác định 4 góc mê cung cho Teleport (di chuyển vào trong 1 ô để tránh tường)
        self.teleport_corners = [
            (1, 1),                         # Top-Left (vào trong 1 ô)
            (1, self.cols - 2),             # Top-Right (vào trong 1 ô)
            (self.rows - 2, 1),             # Bottom-Left (vào trong 1 ô)
            (self.rows - 2, self.cols - 2)  # Bottom-Right (vào trong 1 ô)
        ]

    def is_wall(self, pos):
        """Kiểm tra một vị trí (r, c) có phải là tường '%' không."""
        r, c = pos
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.layout_list[r][c] == '%'
        return True # Ngoài biên coi như tường

    def rotate_90_degrees_right(self):
        """
        Xử lý việc xoay mê cung 90 độ sang phải (yêu cầu của đề bài).
        """
        try:
            # Lưu kích thước cũ để tính toán xoay
            old_rows = self.rows
            old_cols = self.cols
            
            # Cập nhật layout mới (xoay)
            new_rows = self.cols
            new_cols = self.rows
            new_layout = [['' for _ in range(new_cols)] for _ in range(new_rows)]
            
            for r in range(self.rows):
                for c in range(self.cols):
                    # Công thức xoay 90 độ sang phải: (r, c) -> (c, rows - 1 - r)
                    new_r = c
                    new_c = self.rows - 1 - r
                    if 0 <= new_r < new_rows and 0 <= new_c < new_cols:
                        new_layout[new_r][new_c] = self.layout_list[r][c]
                        
            self.layout_list = new_layout
            self.rows = new_rows
            self.cols = new_cols
            
            # Cập nhật lại vị trí các đối tượng sau khi xoay
            self._update_positions_after_rotation(old_rows)
            
        except Exception as e:
            print(f"Error during maze rotation: {e}")
            # Không xoay nếu có lỗi
            pass
    
    def _update_positions_after_rotation(self, old_rows=None):
        """
        Cập nhật vị trí các đối tượng sau khi xoay mê cung.
        """
        # Cập nhật vị trí cổng thoát
        if self.exitgate_pos:
            old_r, old_c = self.exitgate_pos
            # Công thức xoay 90 độ sang phải: (r, c) -> (c, old_rows - 1 - r)
            # Sử dụng old_rows nếu được cung cấp, nếu không thì dùng self.rows
            rows_to_use = old_rows if old_rows is not None else self.rows
            new_r, new_c = old_c, rows_to_use - 1 - old_r
            # Kiểm tra vị trí mới có hợp lệ không
            if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
                self.exitgate_pos = (new_r, new_c)
            else:
                # Nếu vị trí mới không hợp lệ, tìm vị trí gần nhất
                self.exitgate_pos = (min(new_r, self.rows - 1), min(new_c, self.cols - 1))
        
        # Cập nhật lại các góc teleport (di chuyển vào trong 1 ô để tránh tường)
        self.teleport_corners = [
            (1, 1),                         # Top-Left (vào trong 1 ô)
            (1, self.cols - 2),             # Top-Right (vào trong 1 ô)
            (self.rows - 2, 1),             # Bottom-Left (vào trong 1 ô)
            (self.rows - 2, self.cols - 2)  # Bottom-Right (vào trong 1 ô)
        ]
    
    def is_teleport_corner(self, pos):
        """
        Kiểm tra xem vị trí có phải là góc teleport không.
        """
        return pos in self.teleport_corners
    
    def get_teleport_destinations(self, current_pos):
        """
        Lấy danh sách các vị trí teleport có thể đến từ vị trí hiện tại.
        """
        if self.is_teleport_corner(current_pos):
            # Trả về tất cả các góc teleport trừ góc hiện tại
            return [corner for corner in self.teleport_corners if corner != current_pos]
        return []
        
    def eat_wall(self, pos):
            """
            Thay đổi một ô tường '%' thành ô trống ' ' trong layout_list.
            """
            r, c = pos
            # Kiểm tra kỹ trong biên và đúng là tường
            if 0 <= r < self.rows and 0 <= c < self.cols:
                if self.layout_list[r][c] == '%':
                    self.layout_list[r][c] = ' '

# Cập nhật lại vị trí các đối tượng tĩnh như cổng thoát (nếu cần thiết)
# (Đây là phần phức tạp, có thể để lại sau)

    def _save_initial_state(self):
        """
        Lưu trạng thái ban đầu của mê cung để có thể reset.
        """
        # Lưu layout ban đầu
        self.initial_layout = [row[:] for row in self.layout_list]  # Deep copy
        self.initial_rows = self.rows
        self.initial_cols = self.cols
        self.initial_exitgate_pos = self.exitgate_pos
        self.initial_teleport_corners = self.teleport_corners[:]  # Copy list
    
    def reset_to_initial_state(self):
        """
        Reset mê cung về trạng thái ban đầu.
        """
        # Khôi phục layout ban đầu
        self.layout_list = [row[:] for row in self.initial_layout]  # Deep copy
        self.rows = self.initial_rows
        self.cols = self.initial_cols
        self.exitgate_pos = self.initial_exitgate_pos
        self.teleport_corners = self.initial_teleport_corners[:]  # Copy list