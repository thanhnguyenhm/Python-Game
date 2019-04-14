# ----------------------------------------------------------------------
# Name:        Scooter Hunter
# Purpose:     Game Scooter Hunter implementation with tkinter
#
# Author:      Thanh Nguyen
# ----------------------------------------------------------------------
"""
Implement a GUI game with animation in tkinter.

usage: hunter.py [-h] [-v] {easy,normal,hard} [num_scooter] [num_student]
positional arguments:
  {easy,normal,hard}   Choose difficulty level of the game
  num_scooter          How many scooters do you want to hunt?
  num_student          How many students do you want to appear?

optional arguments:
  -h, --help           show this help message and exit
  -v, --verbose        Print details?
"""
import tkinter
import random
import argparse

def get_arguments():
    """
    Parse and validate the command line arguments.
    :return: tuple containing the level (string), num_scooter (int),
         num_student (int) and the verbose option (boolean).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('level',
                        help='Choose difficulty level of the game: ',
                        choices=['easy', 'normal', 'hard'],
                        nargs='?',
                        default='normal')

    parser.add_argument('num_scooter',
                        help='How many scooters do you want to hunt?',
                        type=int,
                        nargs='?',
                        default=7)

    parser.add_argument('num_student',
                        help='How many students do you want to appear?',
                        type=int,
                        nargs='?',
                        default=14)

    parser.add_argument('-v', '--verbose',
                        help='Print details?',
                        action='store_true')

    arguments = parser.parse_args()
    level = arguments.level
    num_scooter = arguments.num_scooter
    num_student = arguments.num_student
    verbose = arguments.verbose
    return level, num_scooter, num_student, verbose

class Game:
    """
    Class to support a GUI with animation.

    Argument:
    parent: (tkinter.Tk) the root window object

    Attributes:
    parent: (tkinter.Tk) the root window object
    canvas: (tkinter.Canvas) A Canvas widget defining the race area.
    """

    # Get command line arguments
    level, num_scooter, num_student, verbose = get_arguments()

    # Class variables
    score = 0  # one score for each scooter collected
    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 700
    if level == 'easy':
        min_speed = 1
        max_speed = 3
    elif level == 'normal':
        min_speed = 2
        max_speed = 4
    elif level == 'hard':
        min_speed = 3
        max_speed = 5
    player_speed = 30
    gate_x0 = 350
    gate_y0 = 630
    gate_x1 = 650
    gate_y1 = 730

    def __init__(self, parent):
        parent.title('Game Scooter Hunter')
        self.parent = parent
        self.result = ''
        self.go = True
        self.spartan = tkinter.PhotoImage(file='spartans.gif')
        self.spartan = self.spartan.subsample(8, 8)
        self.x_pixel = {}
        self.y_pixel = {}

        # make a frame to group all game information objects
        info_frame = tkinter.Frame(parent)

        # add spartans photo
        photo = tkinter.Label(info_frame, image=self.spartan)
        photo.image = self.spartan
        photo.grid(column=0, row=0)

        # add game name
        name = tkinter.Label(info_frame, text='Scooter Hunter',
                             fg='steel blue', width=18)
        name.config(font=('Helvetica', 48, 'bold'))
        name.grid(column=1, row=0)

        # display score
        self.display_score = tkinter.Label(info_frame,
                                           text=f'Score: 'f'{self.score}',
                                           fg='gold', width=10)

        self.display_score.config(font=('Helvetica', 30, 'bold'))
        self.display_score.grid(column=2, row=0)

        # add new game button
        restart_button = tkinter.Button(info_frame, text='New Game', width=10,
                                        command=self.start)
        restart_button.grid(column=3, row=0)

        # register it with a geometry manager
        info_frame.grid()

        # instantiate our Canvas widget with the root as parent
        self.canvas = tkinter.Canvas(parent, width=self.CANVAS_WIDTH,
                                     height=self.CANVAS_HEIGHT,
                                     background='gold')
        # register our canvas with a geometry manager
        self.canvas.grid()

        instruction = (f'Starting a {self.level} level game... Use four'
                       f' arrow keys to move. Try to capture all '
                       f'{self.num_scooter}'
                       f' scooters while avoiding {self.num_student} students'
                       f' walking around the campus.')

        # make a label widget to display rules
        rule = tkinter.Label(parent, text=instruction, height=2)

        self.gate = self.canvas.create_rectangle(self.gate_x0, self.gate_y0,
                                                 self.gate_x1, self.gate_y1,
                                                 fill='steel blue')

        rule.grid()
        self.start()
        self.move_player()

    def start(self):
        self.go = True
        self.score = 0
        if self.result:
            self.canvas.delete(self.result)
        self.display_score.configure(text=f'Score: 'f'{self.score}')
        self.create_scooters(self.num_scooter)
        self.create_students(self.num_student)
        self.x_pixel = {student: random.randint(self.min_speed,
                            self.max_speed) for student in self.student_list}
        self.y_pixel = {student: random.randint(self.min_speed,
                            self.max_speed) for student in self.student_list}
        self.player_image = tkinter.PhotoImage(file='spartan.gif')
        self.player = self.canvas.create_image(500, 670,
                                               image=self.player_image)
        self.animate()
        # self.move_player()

    def move_player(self):
        self.parent.bind('<Left>', self.left)
        self.parent.bind('<Right>', self.right)
        self.parent.bind('<Up>', self.up)
        self.parent.bind('<Down>', self.down)

    def check_collision(self):
        player_coor = self.canvas.coords(self.player)
        for i in self.student_list:
            if (abs(self.canvas.coords(i)[0] - player_coor[0]) <= 15
                    and abs(self.canvas.coords(i)[1] - player_coor[1]) <= 30):
                self.go = False
                self.result = self.canvas.create_text(500, 300,
                            text=f'GAME OVER!\nYOUR SCORE: {self.score}\n'
                          'CLICK NEW GAME TO RESTART', fill='Red')
                return
        for j in self.scooter_list:
            if (abs(self.canvas.coords(j)[0] - player_coor[0]) <= 30
                    and abs(self.canvas.coords(j)[1] - player_coor[1]) <= 30):
                self.score += 1
                self.display_score.configure(text=f'Score: 'f'{self.score}')
                self.scooter_list.remove(j)
                self.canvas.delete(j)
        if not self.scooter_list:
            self.go = False
            self.result = self.canvas.create_text(500, 300,
                          text=f'YOU WON!\nYOUR SCORE: {self.score}\n'
                          'CLICK NEW GAME TO RESTART', fill='Blue')

    def left(self, event):
        if self.go:
            x, y = self.canvas.coords(self.player)
            if x > 30:
                self.canvas.move(self.player, -self.player_speed, 0)

    def right(self, event):
        if self.go:
            x, y = self.canvas.coords(self.player)
            if x < self.CANVAS_WIDTH - 30:
                self.canvas.move(self.player, self.player_speed, 0)

    def up(self, event):
        if self.go:
            x, y = self.canvas.coords(self.player)
            if y > 48:
                self.canvas.move(self.player, 0, -self.player_speed)

    def down(self, event):
        if self.go:
            x, y = self.canvas.coords(self.player)
            if y < self.CANVAS_HEIGHT - 50:
                self.canvas.move(self.player, 0, self.player_speed)

    def create_scooters(self, num):
        self.scooter_image = tkinter.PhotoImage(file='scooter.gif')
        self.scooter_list = []
        for i in range(num):
            x = random.randint(50, self.CANVAS_WIDTH - 50)
            y = random.randint(50, self.CANVAS_HEIGHT - 50)
            self.scooter_list.append(self.canvas.create_image(x, y,
                                      image=self.scooter_image))

    def create_students(self, num):
        self.student_image = tkinter.PhotoImage(file='student.gif')
        self.student_list = []
        for i in range(num):
            x = random.randint(50, self.CANVAS_WIDTH - 50)
            y = random.randint(50, self.CANVAS_HEIGHT - 50)
            self.student_list.append(self.canvas.create_image(x, y,
                                    image=self.student_image))

    def animate(self):
        if self.go:
            self.run(self.student_list)
            self.check_collision()
            self.parent.after(1, self.animate)

    def run(self, students):
        for s in students:
            pix = self.x_pixel[s]
            x, y = self.canvas.coords(s)
            if x >= self.CANVAS_WIDTH:
                self.x_pixel[s] = -abs(pix)
            if x <= 0:
                self.x_pixel[s] = abs(pix)
            if y >= self.CANVAS_HEIGHT:
                self.y_pixel[s] = -abs(pix)
            if y <= 0:
                self.y_pixel[s] = abs(pix)
            if ((self.gate_x0 < x + 20 < self.gate_x1) and
                    (self.gate_y0 < y + 20 < self.gate_y1)):
                self.x_pixel[s] = -abs(pix)
                self.y_pixel[s] = -abs(pix)
            self.canvas.move(s, self.x_pixel[s], self.y_pixel[s])


def main():
    root = tkinter.Tk()  # create the GUI application main window
    scooter_hunter = Game(root)  # instantiate our Game object
    root.mainloop()  # enter the main event loop and wait


if __name__ == '__main__':
    main()
