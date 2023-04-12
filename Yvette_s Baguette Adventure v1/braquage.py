import tkinter as tk
from random import randint

class MiniJeuBraquage:
    def __init__(self, master, global_game=None, node=None):
        self.node = node
        self.global_game = global_game
        self.master = master

    def create_help_frame(self):
        """
        Crée la frame qui explique le jeu au joueur, qui contient également le bouton pour démarrer le jeu
        """    
        self.help_frame = tk.Frame(self.master)
        self.help_frame.pack()
    
        indications_1 = tk.Label(self.help_frame, text = "Yvette pénètre dans le coffre de la banque et elle découvre un coffre rempli d'or !")
        indications_1.pack()

        indications_2 = tk.Label(self.help_frame, text = "Vous devez cliquer dessus le plus rapidement possible pour le vider !")
        indications_2.pack()

        indications_3 = tk.Label(self.help_frame, text = "Faites bien attention au compteur (CPS) en haut de l'écran qui doit rester dans le vert.")
        indications_3.pack()

        next_button = tk.Button(self.help_frame, text="Commencer", command = lambda : self.play())
        next_button.pack()
    
    def play(self):
        self.help_frame.destroy()
        self.bank_frame = tk.Frame(self.master)
        self.bank_frame.pack(expand=1, fill="both")

        self.canvas = tk.Canvas(self.bank_frame, width=1280, height=800)
        self.canvas.pack()

        self.bank_image= tk.PhotoImage(file="image/Mini_Jeu_Braquage/bank_vault.png")
        self.bank_bg = self.canvas.create_image(0, 0, anchor='nw', image=self.bank_image)

        self.chest = Chest(self.canvas, self, self.master)
        self.cps = CPS(self.canvas,self, self.master, self.chest)
        self.master.bind("<Button-1>", self.chest.click)

        self.master.after(10, self.chest.anim)  
        self.master.after(10, self.cps.update, 0)

    def stop_score(self):
        self.cps.stop_score()

    def stop_game(self, type):
        self.bank_frame.destroy()
        if type == "win":
            self.global_game.play(self.node.get_gauche())
        else:
            self.global_game.play(self.node.get_droit())
    

class Chest:
    def __init__(self, canvas, main_app, root):
        self.root = root
        self.main = main_app
        self.canvas = canvas
        self.coins = 100
        self.indice_coin = 0
        self.chest_images = {j : tk.PhotoImage(file=f"image/Mini_Jeu_Braquage/gold_chest_{i}.png").zoom(10) for j,i in zip(range(75,-1,-25),range(1,5))}
        self.emptychest_image = tk.PhotoImage(file=f"image/Mini_Jeu_Braquage/gold_chest_5.png").zoom(10)
        self.stop = False     
        self.step = 0 # utilisé pour bouger le coffre lorsque l'on click
  
    def anim(self):
        if not self.stop:
            self.canvas.delete("chest")
            if self.coins<list(self.chest_images.keys())[self.indice_coin]:
                self.indice_coin += 1
            self.chest_obj = self.canvas.create_image(610, 580, anchor='center', image=self.chest_images[list(self.chest_images.keys())[self.indice_coin]], tag="chest")
            self.root.after(100, self.anim)

    def click(self, event): 
        if not self.stop:
            x = self.canvas.winfo_pointerx()-self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery()-self.canvas.winfo_rooty()
            if 610-160<=x<= 610+160 and 580-150<=y<=580+150:
                self.coins-=1
                self.click_animation()
                coin = Coin(self.canvas,self.root,(randint(0,1250),randint(0,200)))
                coin.spawn_coin()
            if self.coins == 0:
                self.canvas.delete("chest")
                self.chest_obj = self.canvas.create_image(610, 580, anchor='center', image=self.emptychest_image, tag="chest")
                self.stop=True
                self.main.stop_score()

    def click_animation(self):
        if self.step<5:
            self.canvas.move(self.chest_obj,0,-4)
        else:
            self.canvas.move(self.chest_obj,0,4)
        self.step+=1
        if self.step<10:
            self.root.after(10, self.click_animation)
        else:
            self.step=0
    
    def get_nb_click(self):
        return 100 - self.coins

class Coin:
    def __init__(self, canvas, root, start_pos):
        self.root = root
        self.canvas = canvas
        self.start_pos = start_pos
        self.coin_img = tk.PhotoImage(file="image/Mini_Jeu_Braquage/coin.png")
        
    def spawn_coin(self):
        coin = self.canvas.create_image(self.start_pos[0], self.start_pos[1], anchor='center', image=self.coin_img)
        self.move_coin(coin)
    
    def move_coin(self,coin):
        self.canvas.move(coin, 0, 15)
        coin_pos = self.canvas.coords(coin)
        if coin_pos[1] >800:
            self.canvas.delete(coin)
        else:
            self.root.after(20, self.move_coin, coin)
        
class CPS:
    def __init__(self, canvas,main_app, root, chest):
        self.root = root
        self.main = main_app
        self.canvas = canvas
        self.chest = chest
        self.time = 0
        self.cps = 0
        self.score_label = self.canvas.create_text(640,60,text=str(self.cps),fill="white",font=("Agency FB", 100, "bold"))
        self.stop = False
    
    def update(self,total_click):
        if not self.stop:
            self.time += 0.1
            self.cps = round(total_click/self.time,1)
            self.canvas.itemconfig(self.score_label, text=str(self.cps),fill="green" if self.cps >5 else "red")
            self.root.after(100,self.update,self.chest.get_nb_click())
    
    def stop_score(self):
        self.stop = True
        self.root.after(2500,self.main.stop_game, "win" if self.cps>5 else "lose")




