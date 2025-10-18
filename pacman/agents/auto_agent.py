# pacman/agents/auto_agent.py

class AutoAgent:
    """
    Agent sử dụng thuật toán A* để tìm đường đi.
    """
    def __init__(self):
        print("AutoAgent has ready.")
        # TODO: Khởi tạo A* planner
        self.plan = [] # Kế hoạch (danh sách actions)
    
    def process_event(self, event):
        """
        AutoAgent không cần xử lý input từ người dùng,
        nên hàm này không làm gì cả.
        """
        pass 

    def get_action(self, game_state):
        """
        Hàm này được gọi bởi GameEngine sau vòng lặp sự kiện.
        Nó sẽ chạy logic A* (hiện tại là TODO) và trả về hành động.
        """
        # TODO: Logic A*
        # 1. Nếu plan rỗng, chạy A* để tạo plan mới.
        # 2. Lấy hành động tiếp theo từ plan (self.plan.pop(0))
        # 3. Trả về hành động đó
        
        # Tạm thời trả về None (chưa di chuyển)
        return None