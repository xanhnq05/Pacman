# pacman/agents/manual_agent.py

class ManualAgent:
    """
    Agent nhận input từ người dùng qua phím mũi tên.
    """
    def __init__(self):
        print("ManualAgent has ready.")
    
    def get_action(self, game_state):
        # Đây sẽ là nơi đọc input từ Pygame
        return "Manual Action"
    
# pacman/agents/manual_agent.py

class ManualAgent:
    def __init__(self):
        # Không cần logic phức tạp
        pass
    
    def get_action(self, game_state):
        # Trả về None trong chế độ Manual, vì hành động được xử lý trực tiếp 
        # trong vòng lặp Pygame (GameEngine) từ input bàn phím.
        return None