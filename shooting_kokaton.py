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


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    スコアの表示に関するクラス
    """
    def __init__(self,):
        """
        爆弾を撃ち落とした回数のスコア表示
        """
        self.fonto = pg.font.SysFont("hgp創英角ポップ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.high_score = 0
        self.img = self.fonto.render(f"score:{self.score}", 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT-50)
    
    def update(self, screen: pg.Surface):
        """
        スコアの変動を描画する
        引数 screen：画面Surface
        """
        self.img = self.fonto.render(f"score:{self.score}", 0, self.color)
        screen.blit(self.img, self.rct)   
           

class Explosion:
    """
    ビームと爆弾が衝突した際に爆発エフェクトを表示するクラス
    """
    def __init__(self,bomb_rct: pg.Rect):
        """
        爆発エフェクトの画像を設定
        引数：爆弾の位置
        """
        # self.img = pg.image.load("fig/explosion.gif")
        # self.imgs = [self.img,pg.transform.flip(self.img,True,True)]
        # self.rct = self.img.get_rect()
        # self.rct.center = bomb_rct
        # self.life = 2
    
    def update(self, screen: pg.Surface):
        """
        スコアの変動を描画する
        引数 screen：画面Surface
        """
        # self.life -= 1
        # if(self.life > 0):
        #     screen.blit(self.imgs[0], self.rct)
        #     screen.blit(self.imgs[1], self.rct) 


def main():
    pg.display.set_caption("シューティングこうかとん")
    NUM_OF_BOMBS = 5
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    bg_img3 = bg_img
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []  # 複数のビームを格納する
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    tick = 50  # 難易度easyの速度
    state = "START"  # 実行時にスタート画面を表示する

    while True: 
        # スタート画面
        if state == "START":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_q:
                    state = "EXPLANATION"  # ゲーム説明を表示
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
            end_txt = font_select.render("Esc：ゲームを終了する", True, (255, 255, 255))
            high_score_txt = font_score.render(f"ハイスコア：{score.high_score}", True, (255, 255, 255))
            screen.blit(title_txt, [HEIGHT//2-200, WIDTH//2-450])
            screen.blit(start_txt, [HEIGHT//2-200, WIDTH//2-280])
            screen.blit(explanation_txt, [HEIGHT//2-200, WIDTH//2-210])
            screen.blit(end_txt, [HEIGHT//2-200, WIDTH//2-140])
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
            explanation_txt = font_select.render("Q：遊び方説明", True, (255, 255, 255))
            end_txt = font_select.render("Esc：ゲームを終了する", True, (255, 255, 255))
            high_score_txt = font_score.render(f"ハイスコア：{score.high_score}", True, (255, 255, 255))
            screen.blit(title_txt, [HEIGHT//2-200, WIDTH//2-450])
            screen.blit(start_txt, [HEIGHT//2-200, WIDTH//2-280])
            screen.blit(explanation_txt, [HEIGHT//2-200, WIDTH//2-210])
            screen.blit(end_txt, [HEIGHT//2-200, WIDTH//2-140])
            screen.blit(high_score_txt, [HEIGHT//2+500, WIDTH//2+50])

            # ゲーム説明画面描画
            if state == "EXPLANATION":
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
                    beams.append(Beam(bird)) 
            
            screen.blit(bg_img, [-tmr, 0])
            if (tmr >= 500):
                screen.blit(bg_img2, [-tmr+1600, 0])
            if (tmr >= 1600):
                screen.blit(bg_img3, [-tmr+3200, 0])
            if (tmr >= 3199):
                tmr = 0
            
            #if bomb is not None:  # 爆弾が一個の時
            for bomb in bombs:
                if bird.rct.colliderect(bomb.rct):
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    fonto = pg.font.Font(None, 80)
                    txt = fonto.render("Game Over", True, (255, 0, 0))
                    screen.blit(txt, [WIDTH//2-150,HEIGHT//2])
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(2)
                    state = "START"  # 初期化してスタート画面に移動する
                    NUM_OF_BOMBS = 5
                    bird = Bird((300, 200))
                    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
                    beams = []  # 複数のビームを格納する
                    score = Score()
                    tmr = 0
                    
            for i, bomb in enumerate(bombs):
                for beam in beams:
                    if beam.rct.colliderect(bomb.rct):
                        bombs[i] = None
                        beam = None 
                        bird.change_img(6, screen)  # こうかとんが喜ぶエフェクト
                        score.score += 1
                        break

            bombs = [bomb for bomb in bombs if bomb is not None]
            beams = [beam for beam in beams if beam is not None]


            key_lst = pg.key.get_pressed()
            bird.update(key_lst, screen) 
            for beam in beams:  # ビームが存在するときだけ
                beam.update(screen)
                if (beam.rct.left < 0) or (beam.rct.top < 0) or (WIDTH < beam.rct.right) or (HEIGHT < beam.rct.bottom):
                    del beam 
                
            for bomb in bombs:
                bomb.update(screen)
            score.update(screen)
            pg.display.update() 
            tmr += 5
            clock.tick(tick)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()