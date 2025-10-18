# pacman/core/grid.py
import os
import sys

class Grid:
    """
    Biểu diễn mê cung (layout), chứa các thông tin tĩnh như tường, kích thước.
    Cũng xử lý các luật liên quan đến cấu trúc map như Teleport và Xoay.
    """
    def __init__(self, layout_file):
        # Đường dẫn file layout
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

        self._find_initial_objects()

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
                # Trả về list of lists của các ký tự (ví dụ: [['%', '%', ...], [...]])
                return [list(line.strip()) for line in f] 
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file layout tại {full_path}")
            sys.exit()

    def _find_initial_objects(self):
        """
        Tìm và lưu trữ vị trí ban đầu của Pacman, thức ăn, cổng thoát, v.v.
        """
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
        
        # Xác định 4 góc mê cung cho Teleport (đơn giản hóa)
        self.teleport_corners = [
            (0, 0),                         # Top-Left
            (0, self.cols - 1),             # Top-Right
            (self.rows - 1, 0),             # Bottom-Left
            (self.rows - 1, self.cols - 1)  # Bottom-Right
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
        # Cập nhật layout mới (xoay)
        new_rows = self.cols
        new_cols = self.rows
        new_layout = [['' for _ in range(new_cols)] for _ in range(new_rows)]
        
        for r in range(self.rows):
            for c in range(self.cols):
                # Công thức xoay 90 độ sang phải: (r, c) -> (c, new_rows - 1 - r)
                new_layout[c][new_rows - 1 - r] = self.layout_list[r][c]

        self.layout_list = new_layout
        self.rows = new_rows
        self.cols = new_cols
        
        # Cập nhật lại vị trí các đối tượng tĩnh như cổng thoát (nếu cần thiết)
        # (Đây là phần phức tạp, có thể để lại sau)