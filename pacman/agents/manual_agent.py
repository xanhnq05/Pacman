# pacman/agents/manual_agent.py
import pygame

class ManualAgent:
    """
    Agent nhận input từ người dùng qua phím mũi tên.
    Nó đăng ký hành động khi một phím được nhấn (trong process_event)
    và trả về hành động đó khi được GameEngine hỏi (trong get_action).
    """
    def __init__(self):
        print("ManualAgent has ready.")
        self.next_action = None # Sẽ lưu trữ (dr, dc)
        self.teleport_choice = None # Sẽ lưu trữ 1, 2, 3, hoặc 4

    def process_event(self, event):
        """
        Hàm này được gọi bởi GameEngine bên trong vòng lặp sự kiện.
        Nó "lắng nghe" các phím được nhấn và lưu hành động tương ứng.
        """
        # Chỉ xử lý khi phím được NHẤN XUỐNG
        if event.type == pygame.KEYDOWN:
            # Xử lý phím teleportation (1-4)
            if event.key == pygame.K_1:
                self.teleport_choice = 1
            elif event.key == pygame.K_2:
                self.teleport_choice = 2
            elif event.key == pygame.K_3:
                self.teleport_choice = 3
            elif event.key == pygame.K_4:
                self.teleport_choice = 4
            # Xử lý phím di chuyển (mũi tên)
            elif event.key == pygame.K_UP:
                self.next_action = (-1, 0) # (dr, dc) - Lên
            elif event.key == pygame.K_DOWN:
                self.next_action = (1, 0)  # Xuống
            elif event.key == pygame.K_LEFT:
                self.next_action = (0, -1) # Trái
            elif event.key == pygame.K_RIGHT:
                self.next_action = (0, 1)  # Phải
    
    def get_action(self, game_state):
        """
        Hàm này được gọi bởi GameEngine sau vòng lặp sự kiện (mỗi frame).
        Nó trả về hành động đã đăng ký và xóa nó đi (để đảm bảo 1 lần nhấn = 1 lần di chuyển).
        """
        # Lấy hành động đã lưu
        action_to_return = self.next_action
        
        # Xóa hành động (để không lặp lại ở frame sau)
        self.next_action = None 
        
        # Trả về hành động (hoặc None nếu không có phím nào được nhấn)
        return action_to_return