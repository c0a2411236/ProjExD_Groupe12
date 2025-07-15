import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


#pg.sprite.Spriteの追加とそれに応じた書き換え
class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    state = "normal"  # 無敵でない通常状態の変数
    hyper_life = 0  # 無敵時間の変数
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }


    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        # self.
        # self.
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        super().__init__()
        # self.
        # self.
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                if key_lst[pg.K_LSHIFT]:
                    self.speed = 20
                else:
                    self.speed = 10
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        self.image = pg.image.load(f"fig/beam2.png")#爆弾からビームに変更、名前はわかりやすいから爆弾のまま
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(self.image, angle, 1.0)#ビーム角度の変更
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
        # yoko, tate = check_bound(self.rct)
        # if not yoko:
        #     self.vx *= -1
        # if not tate:
        #     self.vy *= -1
        # self.rct.move_ip(self.vx, self.vy)
        # screen.blit(self.img, self.rct)


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        """
        爆弾を撃ち落とした回数のスコア表示
        最高スコアを表示
        """
        self.fonto = pg.font.SysFont("hgp創英角ポップ体", 30)
        self.now_color = (0, 0, 255)
        self.score = 0
        self.now_img = self.fonto.render(f"score:{self.score}", 0, self.now_color)  # 現在の点数
        self.now_rct = self.now_img.get_rect()
        self.now_rct.center = (100, HEIGHT-50)

        self.high_color = (255, 0, 0)
        self.fileobj = open(file = "score.txt", mode = "r", encoding = "utf-8")  # スコア記録ファイルを開く
        self.txt = self.fileobj.read()
        self.fileobj.close()
        if self.txt == '':
            self.fileobj = open("score.txt", "w", encoding="utf-8")
            self.fileobj.write("0")
            self.fileobj.close()
        self.fileobj = open("score.txt", "r", encoding="utf-8")
        self.high_score = int(self.fileobj.read())
        self.fileobj.close()

        self.high_img = self.fonto.render(f"high score:{self.high_score}", 0, self.high_color)  # 最高点数
        self.high_rct = self.high_img.get_rect()
        self.high_rct.center = (100, HEIGHT - 70)

        self.new_fonto = pg.font.SysFont("fantasy", 45)
        self.new_color = (255, 255, 0)
        self.new_img = self.new_fonto.render("New Record!", 0, self.new_color)  # 更新時
        self.new_rct = self.new_img.get_rect()
        self.new_rct.center = (100, HEIGHT - 90)

        self.check_fonto = pg.font.SysFont("hgp創英角ポップ体", 50)
        self.check_img = self.check_fonto.render("Your best score has been reset!", True, (255, 255, 255), (0,0,0))  # 最高スコアリセット通知
        self.check_rct = self.check_img.get_rect()
        self.check_rct.center = (WIDTH//2, HEIGHT//2-100)

        self.kokaton_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1)   # リセット通知時のこうかとん画像
        self.kokaton_rct1 = self.kokaton_img.get_rect()
        self.kokaton_rct2 = self.kokaton_img.get_rect()
        self.kokaton_rct1.center = (WIDTH//2 - 290, HEIGHT//2-100)
        self.kokaton_rct2.center = (WIDTH//2 + 290, HEIGHT//2-100)

    
    def update(self, screen: pg.Surface):
        """
        スコアの変動を描画する
        最高スコアを描画する
        最高スコアの更新を伝える
        引数 screen：画面Surface
        """
        self.now_img = self.fonto.render(f"score:{self.score}", 0, self.now_color)
        screen.blit(self.now_img, self.now_rct)

        if self.high_score < self.score:
            self.high_score = self.score  # 最高スコアを更新
            screen.blit(self.new_img, self.new_rct)
        self.fileobj = open("score.txt", "w", encoding="utf-8")
        self.fileobj.write(f"{self.high_score}")
        self.fileobj.close()
        self.high_img = self.fonto.render(f"high score:{self.high_score}", 0, self.high_color)
        screen.blit(self.high_img, self.high_rct)

    def score_reset(self, screen: pg.Surface):
        """
        記録している最高スコアをリセットする
        最高スコアリセットを知らせる
        """
        self.high_score = 0
        self.check_img = self.check_fonto.render("Your best score has been reset!", True, (0,0,0), (255, 255, 255))
        screen.blit(self.check_img, self.check_rct)
        screen.blit(self.kokaton_img, self.kokaton_rct1)
        screen.blit(self.kokaton_img, self.kokaton_rct2)
        pg.display.update()
        time.sleep(1.5)
        

class Explosion(pg.sprite.Sprite):
    """
    ビームと爆弾が衝突した際に爆発エフェクトを表示するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(random.choice(__class__.imgs), 0, 0.8)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(700, WIDTH), 1
        self.vx, self.vy = 0, +6
        self.bound = random.randint(50, HEIGHT-1)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(40, 240)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.move_ip(self.vx, self.vy)


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 1.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

class Boss(pg.sprite.Sprite):
    """
    ボス敵に関するクラス
    """
    def __init__(self):
        super().__init__()
        img = pg.image.load("fig/alien1.png")
        self.image = pg.transform.rotozoom(img, 0, 2.5)
        self.rect = self.image.get_rect(center=(900, -200))
        self.vy = 2
        self.hp = 20  # ボスの体力
        self.attack_interval = 30  # 攻撃間隔
        self.attack_timer = 0  # タイマー
        self.state = "entering"  # 状態：登場中 or 停止

    def update(self):
        if self.rect.centery < 150:
            self.rect.centery += self.vy

        else:
            self.state = "stopped"  # 停止状態
            self.attack_timer += 1

def main():
    pg.display.set_caption("シューティングこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    bg_img3 = bg_img
    score = Score()
    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()

    boss = None  # ボスインスタンス
    boss_group = pg.sprite.Group()
    boss_spawned = False  # ボス出現フラグ

    tmr = 0
    x = 0

    clock = pg.time.Clock()

    tick_list = [50, 75, 100]  
    l = 0 # 難易度easyの速度
    # ラジオボタンのデータ
    options = ["EASY", "NORMAL", "HARD"]
    radio_buttons = []
    selected_index = 0
    # ラジオボタンの位置と半径を設定
    start_y = 200
    radius = 20
    spacing = 125

    for l, option in enumerate(options):
        center = (465, start_y + l * spacing)
        radio_buttons.append({"label": option, "center": center})

    def draw_radio_button(screen, center, selected):
        # 外円
        pg.draw.circle(screen, (0, 0, 0), center, radius, 2)
        if selected:
            # 内円（選択時）
            pg.draw.circle(screen, (0, 0, 0), center, radius - 4)

    def draw_options():
        for l, btn in enumerate(radio_buttons):
            draw_radio_button(screen, btn["center"], l == selected_index)
    state = "START"  # 実行時にスタート画面を表示する

    while True: 
        key_lst = pg.key.get_pressed()
        # スタート画面
        if state == "START":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_q:
                    state = "EXPLANATION"  # ゲーム説明を表示
                if event.type == pg.KEYDOWN and event.key == pg.K_d:
                    state = "DIFFICULTY"  # ゲーム説明を表示
                if event.type == pg.KEYDOWN and event.key == pg.K_r:  # rキーで最高スコアをリセット
                    score.score_reset(screen)  # 二重whileループの外側に入れる
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    state = "PLAY"  # ゲーム本編へ

            # スタート画面描画
            start = pg.Surface((WIDTH,HEIGHT))
            start.fill((0, 0, 0))
            start.set_alpha(150)
            screen.blit(start,[0, 0])
            font_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 60)
            font_select = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)
            font_score = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 25)
            title_txt = font_title.render("シューティングこうかとん（仮）", True, (255, 255, 255))   
            start_txt = font_select.render("Enter：ゲームスタート", True, (255, 255, 255))
            explanation_txt = font_select.render("Q：このゲームについて", True, (255, 255, 255))
            difficulty_txt = font_select.render("D：難易度選択", True, (255, 255, 255))
            end_txt = font_select.render("Esc：ゲームを終了する", True, (255, 255, 255))
            high_score_txt = font_score.render(f"ハイスコア：{score.high_score}", True, (255, 255, 255))
            screen.blit(title_txt, [HEIGHT//2-200, WIDTH//2-450])
            screen.blit(start_txt, [HEIGHT//2-200, WIDTH//2-280])
            screen.blit(explanation_txt, [HEIGHT//2-200, WIDTH//2-210])
            screen.blit(difficulty_txt, [HEIGHT//2-200, WIDTH//2-140])
            screen.blit(end_txt, [HEIGHT//2-200, WIDTH//2-70])
            screen.blit(high_score_txt, [HEIGHT//2+500, WIDTH//2+50])
            
            pg.display.update()
        
        if state == "EXPLANATION":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_q:
                    state = "START"  # スタート画面に戻る

            # スタート画面描画
            start = pg.Surface((WIDTH,HEIGHT))
            start.fill((0, 0, 0))
            start.set_alpha(150)
            screen.blit(start,[0, 0])
            font_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 60)
            font_select = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)
            font_score = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 25)
            title_txt = font_title.render("シューティングこうかとん（仮）", True, (255, 255, 255))   
            start_txt = font_select.render("Enter：ゲームスタート", True, (255, 255, 255))
            explanation_txt = font_select.render("Q：このゲームについて", True, (255, 255, 255))
            difficulty_txt = font_select.render("D：難易度選択", True, (255, 255, 255))
            end_txt = font_select.render("Esc：ゲームを終了する", True, (255, 255, 255))
            high_score_txt = font_score.render(f"ハイスコア：{score.high_score}", True, (255, 255, 255))
            screen.blit(title_txt, [HEIGHT//2-200, WIDTH//2-450])
            screen.blit(start_txt, [HEIGHT//2-200, WIDTH//2-280])
            screen.blit(explanation_txt, [HEIGHT//2-200, WIDTH//2-210])
            screen.blit(difficulty_txt, [HEIGHT//2-200, WIDTH//2-140])
            screen.blit(end_txt, [HEIGHT//2-200, WIDTH//2-70])
            screen.blit(high_score_txt, [HEIGHT//2+500, WIDTH//2+50])

            # ゲーム説明画面描画
            pg.draw.rect(screen,(255,255,255),pg.Rect(175,40,750,570),0,border_radius=15)
            font_exp_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)
            font_exp = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
            font_list = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 25)
            exp_title_txt = font_exp_title.render("遊び方", True, (0, 0, 0))
            exp_txt1 = font_exp.render("・方向キーで移動", True, (0, 0, 0))
            exp_txt2 = font_exp.render("・スペースキーでビーム攻撃", True, (0, 0, 0))
            exp_txt3 = font_exp.render("・スコアリスト", True, (0, 0, 0))
            exp_list1 = font_list.render("爆弾 ... １点", True, (0, 0, 0))
            exp_list2 = font_list.render("敵機 ... １０点", True, (0, 0, 0))
            exp_list3 = font_list.render("ボス ... １００点", True, (0, 0, 0))
            exp_txt4 = font_exp.render("Q：タイトルに戻る", True, (0, 0, 0))
            screen.blit(exp_title_txt,[185,50])
            screen.blit(exp_txt1,[185,120])
            screen.blit(exp_txt2,[185,190])
            screen.blit(exp_txt3,[185,260])
            screen.blit(exp_list1,[220,310])
            screen.blit(exp_list2,[220,360])
            screen.blit(exp_list3,[220,410])
            screen.blit(exp_txt4,[655,565])
            
            pg.display.update()

        if state == "DIFFICULTY":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_d:
                    state = "START"  # スタート画面に戻る
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # 左クリック
                    mouse_x, mouse_y = event.pos
                    for l, btn in enumerate(radio_buttons):
                        cx, cy = btn["center"]
                        dist_sq = (mouse_x - cx) ** 2 + (mouse_y - cy) ** 2
                        if dist_sq <= radius ** 2:
                            selected_index = l
                            print(f"選択: {options[selected_index]}")
                            print(selected_index)

            # スタート画面描画
            start = pg.Surface((WIDTH,HEIGHT))
            start.fill((0, 0, 0))
            start.set_alpha(150)
            screen.blit(start,[0, 0])
            font_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 60)
            font_select = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)
            font_score = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 25)
            title_txt = font_title.render("シューティングこうかとん（仮）", True, (255, 255, 255))   
            start_txt = font_select.render("Enter：ゲームスタート", True, (255, 255, 255))
            explanation_txt = font_select.render("Q：遊び方説明", True, (255, 255, 255))
            difficulty_txt = font_select.render("D：難易度選択", True, (255, 255, 255))
            end_txt = font_select.render("Esc：ゲームを終了する", True, (255, 255, 255))
            high_score_txt = font_score.render(f"ハイスコア：{score.high_score}", True, (255, 255, 255))
            screen.blit(title_txt, [HEIGHT//2-200, WIDTH//2-450])
            screen.blit(start_txt, [HEIGHT//2-200, WIDTH//2-280])
            screen.blit(explanation_txt, [HEIGHT//2-200, WIDTH//2-210])
            screen.blit(difficulty_txt, [HEIGHT//2-200, WIDTH//2-140])
            screen.blit(end_txt, [HEIGHT//2-200, WIDTH//2-70])
            screen.blit(high_score_txt, [HEIGHT//2+500, WIDTH//2+50])

            # 難易度選択画面描画
            pg.draw.rect(screen,(255,255,255),pg.Rect(175,40,750,570),0,border_radius=15)
            font_dif_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)
            font_dif = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)
            font_exp = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
            dif_title_txt = font_dif_title.render("～難易度選択～", True, (0, 0, 0))
            dif_txt1 = font_dif.render("　Easy", True, (0, 0, 0))
            dif_txt2 = font_dif.render("　Normal", True, (0, 0, 0))
            dif_txt3 = font_dif.render("　Hard", True, (0, 0, 0))
            exp_txt4 = font_exp.render("D：タイトルに戻る", True, (0, 0, 0))
            screen.blit(dif_title_txt,[375,50])
            screen.blit(dif_txt1,[450,175])
            screen.blit(dif_txt2,[450,300])
            screen.blit(dif_txt3,[450,425])
            screen.blit(exp_txt4,[655,565])
            # 難易度選択ラジオボタン
            draw_options()
            pg.display.update()

        # ゲーム中にescキーを押したら一時停止する
        if state == "STOP":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    state = "PLAY"
            # 画面左上に一時停止を表示
            font_stop = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
            stop_txt = font_stop.render("一時停止中...", True, (255, 255, 255))
            screen.blit(stop_txt, [HEIGHT//2-200, WIDTH//2-450])
            pg.display.update()


        # ゲーム中の動作
        if state == "PLAY":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    state = "STOP"  # ecsキーで一時停止
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    beams.add(Beam(bird)) 
                    
            screen.blit(bg_img, [-x, 0])
            if (x >= 500):
                screen.blit(bg_img2, [-x+1600, 0])
            if (x >= 1600):
                screen.blit(bg_img3, [-x+3200, 0])
            if (x >= 3199):
                x = 0
            if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
                emys.add(Enemy())
            
            for emy in emys:
                if emy.state == "stop" and tmr%emy.interval == 0:
                    # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                    bombs.add(Bomb(emy, bird))

            for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():  # ビームと衝突した敵機リスト
                exps.add(Explosion(emy, 100))  # 爆発エフェクト
                score.score += 10  # 10点アップ
                bird.change_img(6, screen)  # こうかとん喜びエフェクト

            if score.score >= 50 and not boss_spawned:
                boss = Boss()
                boss_group.add(boss)
                boss_spawned = True

            if boss is not None:
                for beam in pg.sprite.spritecollide(boss, beams, True):
                    boss.hp -= 1
                    if boss.hp <= 0:
                        exps.add(Explosion(boss, 100))
                        boss.kill()
                        boss = None
                        score.score += 100  # ボス撃破で+100点
                        bird.change_img(6, screen)  # 喜びエフェクト
            
            if boss is not None:
                if bird.rect.colliderect(boss.rect):
                    bird.change_img(8, screen)
                    score.update(screen)
                    pg.display.update()
                    time.sleep(2)
                    score = Score()
                    bird = Bird(3, (900, 400))
                    bombs = pg.sprite.Group()
                    beams = pg.sprite.Group()
                    exps = pg.sprite.Group()
                    emys = pg.sprite.Group()
                    boss = None  # ボスインスタンス
                    boss_group = pg.sprite.Group()
                    boss_spawned = False  # ボス出現フラグ
                    boss_group.update()
                    boss_group.draw(screen)
                    tmr = 0
                    
            
            if  boss is not None and boss.state == "stopped":
                if boss.attack_timer >= boss.attack_interval:
                    bombs.add(Bomb(boss, bird))  # ボスから爆弾発射
                    boss.attack_timer = 0  # タイマーリセット

            for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():  # ビームと衝突した爆弾リスト
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.score += 1  # 1点アップ

            for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150,HEIGHT//2])
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(2)
                state = "START"  # 初期化してスタート画面に移動する
                score = Score()
                bird = Bird(3, (900, 400))
                bombs = pg.sprite.Group()
                beams = pg.sprite.Group()
                exps = pg.sprite.Group()
                emys = pg.sprite.Group()
                boss = None  # ボスインスタンス
                boss_group = pg.sprite.Group()
                boss_spawned = False  # ボス出現フラグ
                boss_group.update()
                boss_group.draw(screen)
                tmr = 0
                    
            for emy in pg.sprite.spritecollide(bird, emys, True):  # こうかとんと衝突した敵リスト
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150,HEIGHT//2])
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(2)
                state = "START"  # 初期化してスタート画面に移動する
                score = Score()
                bird = Bird(3, (900, 400))
                bombs = pg.sprite.Group()
                beams = pg.sprite.Group()
                exps = pg.sprite.Group()
                emys = pg.sprite.Group()
                boss = None  # ボスインスタンス
                boss_group = pg.sprite.Group()
                boss_spawned = False  # ボス出現フラグ
                boss_group.update()
                boss_group.draw(screen)
                tmr = 0

                # key_lst = pg.key.get_pressed()
                # bird.update(key_lst, screen) 
                # for beam in beams:  # ビームが存在するときだけ
                #     beam.update(screen)
                #     if (beam.rct.left < 0) or (beam.rct.top < 0) or (WIDTH < beam.rct.right) or (HEIGHT < beam.rct.bottom):
                #         del beam 
                    
                # for bomb in bombs:
                #     bomb.update(screen)
            bird.update(key_lst, screen)
            beams.update()
            beams.draw(screen)
            emys.update()
            emys.draw(screen)
            bombs.update()
            bombs.draw(screen)
            exps.update()
            exps.draw(screen)
            score.update(screen)
            boss_group.update()
            boss_group.draw(screen)
            pg.display.update() 
            tmr += 1
            x += 4
            clock.tick(tick_list[selected_index])

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()