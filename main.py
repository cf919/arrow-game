import pygame
import sys
# 常量定义
WIDTH = 800
HEIGHT = 600
GRID_SIZE = 80
GRID_OFFSET_X = 80
GRID_OFFSET_Y = 120
MAX_MISTAKE = 3


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
BLUE = (30, 80, 220)
RED = (220, 30, 30)
YELLOW = (255, 200, 0)
# 游戏状态
STATE_START = 0
STATE_PLAY = 1
STATE_WIN = 2
STATE_LOSE = 3
# 方向常量
DIR_RIGHT = 0
DIR_UP = 1
DIR_DOWN = 2
DIR_LEFT = 3
# 方向偏移：(行变化, 列变化)
DIR_DELTA = [
    (0, 1),   # 右
    (-1, 0),  # 上
    (1, 0),   # 下
    (0, -1)   # 左
]
# 方向像素增量（飞行动画每帧移动像素）
DIR_PIXEL_DELTA = [
    (6, 0),   # 右
    (0, -6),  # 上
    (0, 6),   # 下
    (-6, 0)   # 左
]
# 方向符号
DIR_SYMBOL = {
    DIR_RIGHT: "→",
    DIR_UP: "↑",
    DIR_DOWN: "↓",
    DIR_LEFT: "←"
}
class Arrow:
    def __init__(self, row, col, dire):
        self.row = row
        self.col = col
        self.dir = dire
        self.flash_timer = 0
        self.flying = False
        # 动画坐标，静止时等于格子中心
        self.anim_x, self.anim_y = self.get_center()
    def get_center(self):
        x = GRID_OFFSET_X + self.col * GRID_SIZE + GRID_SIZE // 2
        y = GRID_OFFSET_Y + self.row * GRID_SIZE + GRID_SIZE // 2
        return x, y
    def get_rect(self):
        return pygame.Rect(
            GRID_OFFSET_X + self.col * GRID_SIZE,
            GRID_OFFSET_Y + self.row * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
    def get_color(self):
        if self.flash_timer > 0:
            return RED
        return BLUE
    def start_fly(self):
        self.flying = True
        self.anim_x, self.anim_y = self.get_center()
    def update_anim(self):
        if not self.flying:
            return
        dx, dy = DIR_PIXEL_DELTA[self.dir]
        self.anim_x += dx
        self.anim_y += dy
    def is_out_of_screen(self):
        # 判断飞出可视区域
        return not (0 < self.anim_x < WIDTH and 0 < self.anim_y < HEIGHT)
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()
        self.state = STATE_START
        self.cur_level = 0
        self.arrows = []
        self.mistake_left = MAX_MISTAKE
        self.arrow_remain = 0
        self.font_big = pygame.font.SysFont("simhei", 36)
        self.font_mid = pygame.font.SysFont("simhei", 28)
        self.font_arrow = pygame.font.SysFont("simhei", 42)
        # 【修改】游玩界面重新开始按钮放在右上角，避开棋盘，不遮挡方格
        self.btn_restart = pygame.Rect(WIDTH - 140, 10, 130, 45)
        self.start_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 60)
        self.next_level_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60)
        # 三个关卡：(行, 列, 方向)
        self.levels = [
            [
                Arrow(1, 1, DIR_RIGHT),
                Arrow(1, 4, DIR_UP),
                Arrow(3, 2, DIR_DOWN),
                Arrow(4, 5, DIR_LEFT),
            ],
            [
                Arrow(0, 2, DIR_RIGHT),
                Arrow(2, 0, DIR_DOWN),
                Arrow(3, 4, DIR_LEFT),
                Arrow(5, 1, DIR_UP),
                Arrow(1, 3, DIR_RIGHT),
            ],
            [
                Arrow(0, 0, DIR_DOWN),
                Arrow(1, 5, DIR_LEFT),
                Arrow(2, 2, DIR_UP),
                Arrow(4, 1, DIR_RIGHT),
                Arrow(5, 4, DIR_DOWN),
                Arrow(3, 3, DIR_LEFT),
            ]
        ]
    def load_level(self, idx):
        self.arrows = []
        for a in self.levels[idx]:
            self.arrows.append(Arrow(a.row, a.col, a.dir))
        self.arrow_remain = len(self.arrows)
        self.mistake_left = MAX_MISTAKE
        self.state = STATE_PLAY
    def draw_start(self):
        self.screen.fill(WHITE)
        title = self.font_big.render("一箭又一箭", True, BLACK)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 160))
        pygame.draw.rect(self.screen, BLUE, self.start_btn)
        btn_text = self.font_mid.render("开始游戏", True, WHITE)
        self.screen.blit(
            btn_text,
            (
                self.start_btn.x + self.start_btn.width // 2 - btn_text.get_width() // 2,
                self.start_btn.y + self.start_btn.height // 2 - btn_text.get_height() // 2,
            )
        )
        pygame.display.flip()
    def draw_game(self):
        self.screen.fill(WHITE)
        text_lv = self.font_big.render(f"关卡：{self.cur_level + 1}", True, BLACK)
        text_arrow = self.font_big.render(f"剩余箭头：{self.arrow_remain}", True, BLACK)
        text_mistake = self.font_big.render(f"剩余失误：{self.mistake_left}", True, RED)
        self.screen.blit(text_lv, (20, 10))
        self.screen.blit(text_arrow, (20, 45))
        self.screen.blit(text_mistake, (20, 80))

        # 【新增】游戏进行界面绘制右上角重新开始按钮
        pygame.draw.rect(self.screen, YELLOW, self.btn_restart)
        rt = self.font_mid.render("重新开始", True, BLACK)
        self.screen.blit(
            rt,
            (
                self.btn_restart.x + self.btn_restart.width // 2 - rt.get_width() // 2,
                self.btn_restart.y + self.btn_restart.height // 2 - rt.get_height() // 2,
            )
        )

        # 绘制网格
        for r in range(6):
            for c in range(6):
                rect = pygame.Rect(
                    GRID_OFFSET_X + c * GRID_SIZE,
                    GRID_OFFSET_Y + r * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )
                pygame.draw.rect(self.screen, BLACK, rect, 2)
        # 绘制箭头
        for ar in self.arrows:
            color = ar.get_color()
            symbol = DIR_SYMBOL[ar.dir]
            text = self.font_arrow.render(symbol, True, color)
            # 飞行状态使用动画坐标；静止使用格子中心
            if ar.flying:
                x, y = ar.anim_x, ar.anim_y
            else:
                x, y = ar.get_center()
            self.screen.blit(
                text,
                (
                    x - text.get_width() // 2,
                    y - text.get_height() // 2
                )
            )
        pygame.display.flip()
    def draw_win(self):
        self.screen.fill(WHITE)
        if self.cur_level + 1 >= len(self.levels):
            t = self.font_big.render("全部通关！", True, BLUE)
        else:
            t = self.font_big.render("本关通关！", True, BLUE)
            pygame.draw.rect(self.screen, BLUE, self.next_level_btn)
            btn_text = self.font_mid.render("下一关", True, WHITE)
            self.screen.blit(
                btn_text,
                (
                    self.next_level_btn.x + self.next_level_btn.width // 2 - btn_text.get_width() // 2,
                    self.next_level_btn.y + self.next_level_btn.height // 2 - btn_text.get_height() // 2,
                )
            )
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 40))
        pygame.display.flip()
    def draw_lose(self):
        self.screen.fill(WHITE)
        t = self.font_big.render("游戏失败", True, RED)
        tip = self.font_mid.render("点击重新开始重试本关", True, GRAY)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
        self.screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 10))
        # 失败界面也绘制重启按钮
        pygame.draw.rect(self.screen, YELLOW, self.btn_restart)
        rt = self.font_mid.render("重新开始", True, BLACK)
        self.screen.blit(
            rt,
            (
                self.btn_restart.x + self.btn_restart.width // 2 - rt.get_width() // 2,
                self.btn_restart.y + self.btn_restart.height // 2 - rt.get_height() // 2,
            )
        )
        pygame.display.flip()
    def find_path_target(self, arrow):
        """沿箭头方向路径检测，返回路径上第一个阻挡箭头；没有阻挡返回 None"""
        dr, dc = DIR_DELTA[arrow.dir]
        cr = arrow.row + dr
        cc = arrow.col + dc
        while 0 <= cr < 6 and 0 <= cc < 6:
            for target in self.arrows:
                if target is not arrow and target.row == cr and target.col == cc:
                    return target
            cr += dr
            cc += dc
        return None
    def handle_click_grid(self, mx, my):
        clicked_arrow = None
        for ar in self.arrows:
            if ar.get_rect().collidepoint(mx, my) and not ar.flying:
                clicked_arrow = ar
                break
        if clicked_arrow is None:
            return
        target = self.find_path_target(clicked_arrow)
        if target is not None:
            # 前方有遮挡：闪红提示，扣除失误
            clicked_arrow.flash_timer = 15
            self.mistake_left -= 1
            if self.mistake_left <= 0:
                self.state = STATE_LOSE
        else:
            # 前方无遮挡：启动飞行动画，不扣失误
            clicked_arrow.start_fly()
    def update(self):
        # 更新闪烁计时
        for ar in self.arrows:
            if ar.flash_timer > 0:
                ar.flash_timer -= 1
            if ar.flying:
                ar.update_anim()
        # 飞出屏幕的箭头移除
        remove_list = []
        for ar in self.arrows:
            if ar.flying and ar.is_out_of_screen():
                remove_list.append(ar)
        for ar in remove_list:
            self.arrows.remove(ar)
        self.arrow_remain = len(self.arrows)
        if self.arrow_remain <= 0 and self.state == STATE_PLAY:
            self.state = STATE_WIN
    def run(self):
        while True:
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == STATE_START:
                        if self.start_btn.collidepoint(mx, my):
                            self.cur_level = 0
                            self.load_level(0)
                    elif self.state == STATE_PLAY:
                        #【新增】游玩状态：优先判断点击重新开始按钮
                        if self.btn_restart.collidepoint(mx, my):
                            self.load_level(self.cur_level)
                        else:
                            self.handle_click_grid(mx, my)
                    elif self.state == STATE_WIN:
                        if self.cur_level + 1 < len(self.levels):
                            if self.next_level_btn.collidepoint(mx, my):
                                self.cur_level += 1
                                self.load_level(self.cur_level)
                    elif self.state == STATE_LOSE:
                        if self.btn_restart.collidepoint(mx, my):
                            self.load_level(self.cur_level)
            self.update()
            if self.state == STATE_START:
                self.draw_start()
            elif self.state == STATE_PLAY:
                self.draw_game()
            elif self.state == STATE_WIN:
                self.draw_win()
            elif self.state == STATE_LOSE:
                self.draw_lose()
            self.clock.tick(60)
if __name__ == "__main__":
    try:
        g = Game()
        g.run()
    except Exception as e:
        print(e)
        input("按回车退出")
