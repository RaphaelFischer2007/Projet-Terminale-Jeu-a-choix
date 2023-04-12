import tkinter as tk
import random
from PIL import Image, ImageTk

class MiniJeuCourse:
    def __init__(self, master,global_game,node,mode):
        self.node = node
        self.global_game = global_game
        self.master = master
        self.mode = mode
    def create_help_frame(self):
        """
        Crée la frame qui explique le jeu au joueur, qui contient également le bouton pour démarrer le jeu
        """    
        self.help_frame = tk.Frame(self.master)
        self.help_frame.pack()
        
        if self.mode == "braquage":
            indications_1 = tk.Label(self.help_frame, text = "Vous attendez dans un fourgon à la sortie de la banque.")
            indications_1.pack()
            
            indications_2 = tk.Label(self.help_frame, text = "Soudain, les braqueurs sortent de la banque et s'installe dans le véhicule.")
            indications_2.pack()

            indications_3 = tk.Label(self.help_frame, text = "Vous entendez des sirènes au loin, il faut vite vous échapper.")
            indications_3.pack()

            indications_4 = tk.Label(self.help_frame, text = "Vous devez survivre 30s, en utilisant les flèches directionnelles pour éviter les voitures de police.")
            indications_4.pack()
            
        else:
            indications_1 = tk.Label(self.help_frame, text = "Pas de chance, un passant vous a vu et alerte la police,")
            indications_1.pack()
            
            indications_2 = tk.Label(self.help_frame, text = "Yvette décide de partir en course poursuite !")
            indications_2.pack()

            indications_3 = tk.Label(self.help_frame, text = "Vous devez survivre 30s, en utilisant les flèches directionnelles pour éviter les voitures de police.")
            indications_3.pack()

        next_button = tk.Button(self.help_frame, text="Commencer", command = lambda : self.play())
        next_button.pack()

    
    def play(self):
        self.help_frame.destroy()
        self.race_frame = tk.Frame(self.master)
        self.race_frame.pack(expand=1, fill="both")

        self.canvas = tk.Canvas(self.race_frame, width=1280, height=800)
        self.canvas.pack()

        self.trottoir= tk.PhotoImage(file="image/Mini_Jeu_Course_Poursuite/trottoir.png")
        self.trottoir_gauche = self.canvas.create_image(0, 0, anchor='nw', image=self.trottoir)
        self.trottoir_droite = self.canvas.create_image(1280, 0, anchor='ne', image=self.trottoir)

        self.player = Main_car(self.canvas, self, self.master, self.mode)
        self.road = Road(self.canvas, self.master)
        self.obstacles = Obstacles(self.canvas, self.master)
        self.score = Score(self.canvas, self, self.master)

        self.master.bind("<Left>",self.player.left)
        self.master.bind("<Right>",self.player.right)
        self.master.bind("<Up>",self.player.up)
        self.master.bind("<Down>",self.player.down)
        self.master.bind("e",self.player.test)

        self.master.after(500, self.road.anim) 
        self.master.after(500, self.road.spawn_trees_loop)
        self.master.after(2000, self.obstacles.spawn_police_loop)
        self.master.after(500, self.player.anim)
        self.master.after(2000,self.score.update)        
    
    def stop_animation(self, type):
        if type == "lose":
            self.road.stop_road()
            self.obstacles.stop_obstacles()
            self.score.stop_score()
        else:
            self.road.stop_road()
            self.obstacles.stop_obstacles()
            self.player.stop_win()

    def stop_game(self, type):
        self.race_frame.destroy()
        if type == "win":
            self.global_game.play(self.node.get_gauche())
        else:
            self.global_game.play(self.node.get_droit())

class Road:
    def __init__(self, canvas, root):
        self.root = root
        self.canvas = canvas
        self.road_images = [tk.PhotoImage(file=f"image/Mini_Jeu_Course_Poursuite/road_{i}.png").zoom(2, 4) for i in range(1, 12)]
        self.road_labels = [canvas.create_image(156, 800 * i, anchor='nw', image=img) for i, img in enumerate(self.road_images)]
        self.counter = 1
        self.tree_img = tk.PhotoImage(file="image/Mini_Jeu_Course_Poursuite/tree_1.png")
        self.road_bg = canvas.create_image(156, 0, anchor='nw', image=self.road_images[0], tags='road')  # Create the initial road background
        self.stop = False
    
    def anim(self):
        if not self.stop:
            # Update the background image
            bg = self.road_images[self.counter - 1]
            self.canvas.itemconfig(self.road_bg, image=bg)  # Update the existing road background image
            
            self.counter += 1
            if self.counter == 12:
                self.counter = 1

            self.root.after(200, self.anim)
    
    def spawn_trees(self):
        side = random.choice([0, 1])
        tree_positions = [random.randint(30, 80) if side == 0 else random.randint(1180, 1220), 0]  
        tree = self.canvas.create_image(tree_positions[0], tree_positions[1], anchor='nw', image=self.tree_img)
        self.move_trees(tree, side)
    
    def move_trees(self,tree,side):
        if not self.stop:
            self.canvas.move(tree, 0, 8)
            tree_pos = self.canvas.coords(tree)
            
            if tree_pos[1] >800:
                self.canvas.delete(tree)
            else:
                self.root.after(20, self.move_trees, tree, side)

    def spawn_trees_loop(self):
        if not self.stop:
            self.spawn_trees()
            self.root.after(3500, self.spawn_trees_loop)
    
    def stop_road(self):
        self.stop = True

class Main_car:
    def __init__(self, canvas, main_app, root, mode):
        self.root = root
        self.main = main_app
        self.canvas = canvas
        if mode == "braquage":
            self.main_car_img = tk.PhotoImage(file="image/Mini_Jeu_Course_Poursuite/voitures/Mini_van.png")
        else:
            self.main_car_img = tk.PhotoImage(file="image/Mini_Jeu_Course_Poursuite/voitures/Tesla.png")
        self.mode=mode
        self.explosion_images = [tk.PhotoImage(file=f"image/Mini_Jeu_Course_Poursuite/explosion/explosion_{i}.png").zoom(2) for i in range(6)]
        self.counter = 0
        self.x = random.choice([220,400,610,800])
        self.y = 550
        self.test_on = False
        self.stop = False
        
        
    def anim(self):
        if not self.stop:
            self.canvas.delete("main_car")
            self.main_car = self.canvas.create_image(self.x, self.y, anchor="nw", image=self.main_car_img, tags="main_car") 
            if self.test_on:
                player = self.canvas.coords(self.main_car)
                self.canvas.delete("test")
                if self.mode == "braquage":
                    test_rectangle = self.canvas.create_rectangle((player[0]+85),(player[1]+35),(player[0]+155),(player[1]+220),fill= "blue",tag="test") 
                else:
                    test_rectangle = self.canvas.create_rectangle((player[0]+85),(player[1]+35),(player[0]+166),(player[1]+232),fill= "blue",tag="test") 
                overlapping_items = self.canvas.find_overlapping(*self.canvas.coords(test_rectangle))
                print(overlapping_items)
            else:
                player = self.canvas.coords(self.main_car)
                if self.mode == "braquage":
                    overlapping_items = self.canvas.find_overlapping((player[0]+85),(player[1]+35),(player[0]+155),(player[1]+220))
                else:
                    overlapping_items = self.canvas.find_overlapping((player[0]+85),(player[1]+35),(player[0]+166),(player[1]+232))
                if len(overlapping_items)>3 and 4 not in overlapping_items: 
                    self.stop_explosion()
                    self.stop=True 
                    self.main.stop_animation("lose")
                    
            if not self.stop:
                self.root.after(50, self.anim)

    def left(self, event): 
        if self.canvas.coords(self.main_car)[0]>150:
            self.x -= 25

    def right(self, event):
        if self.canvas.coords(self.main_car)[0]<860:
            self.x += 25

    def up(self, event):
        if self.canvas.coords(self.main_car)[1]>0:
            self.y -= 25

    def down(self, event):
        if self.canvas.coords(self.main_car)[1]<530:
            self.y += 25
    
    def test(self, event):
        if not(self.test_on):
            self.test_on=True
        else:
            self.test_on=False
            self.canvas.delete("test")

    def stop_explosion(self):
        if self.counter==0:
            player = self.canvas.coords(self.main_car)
            self.explosion = self.canvas.create_image(player[0]+90, player[1]+21, anchor='nw', image=self.explosion_images[0], tags='explosion')  # Create the initial road background
            self.counter +=1
        else:
            explosion_img = self.explosion_images[self.counter]
            self.canvas.itemconfig(self.explosion, image=explosion_img)  # Update the existing road background image
            self.counter += 1
        if self.counter < 6:
            self.root.after(100, self.stop_explosion)
    
    def stop_win(self):
        self.stop = True

            
class Obstacles:
    def __init__(self, canvas, root):
        self.root = root
        self.police_img = tk.PhotoImage(file="image/Mini_Jeu_Course_Poursuite/voitures/Police.png")
        self.nb_police = 0
        self.canvas = canvas
        self.stop=False
    def spawn_police(self):
        police_position = [random.choice([295,480,690,880]),0]
        police = self.canvas.create_image(police_position[0], police_position[1], anchor='nw', image=self.police_img)
        self.nb_police +=1
        self.move_police(police)
    
    def move_police(self,police):
        if not self.stop:
            self.canvas.move(police, 0, 8)
            police_pos = self.canvas.coords(police)
            if police_pos[1] >800:
                self.canvas.delete(police)
                self.nb_police -= 1
            else:
                self.root.after(20, self.move_police, police)

    def spawn_police_loop(self):
        if not self.stop:
            if self.nb_police<3:
                self.spawn_police()
            self.root.after(2000, self.spawn_police_loop)
    
    def stop_obstacles(self):
        self.stop=True

class Score:
    def __init__(self, canvas,main_app, root):
        self.root = root
        self.main = main_app
        self.canvas = canvas
        self.score_txt = '0'
        self.score_label = self.canvas.create_text(640,60,text=self.score_txt,fill="white",font=("Agency FB", 100, "bold"))
        self.stop = False
    def update(self):
        if not self.stop:
            self.score_txt=str(int(self.score_txt)+1)
            self.canvas.itemconfig(self.score_label, text=self.score_txt)
            if self.score_txt == "30":
                self.canvas.itemconfig(self.score_label, text="Yvette s'est échappée")
                self.stop = True
                self.main.stop_animation("win")
                self.root.after(1500,self.main.stop_game, "win")

            self.root.after(1000,self.update)
    
    def stop_score(self):
        self.stop = True
        self.canvas.itemconfig(self.score_label, text="Yvette n'a pas pu s'échapper")
        self.root.after(1800,self.main.stop_game, "lose")


