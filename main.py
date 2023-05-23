from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y}"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы поля"


class BoardAlreadyShotException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту точку"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, leng, orientation, lives):
        self.bow = bow
        self.leng = leng
        self.orientation = orientation
        self.lives = lives

    def dots(self):
        ship_dots = []
        for i in range(self.leng):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 1:
                cur_x += 1
            if self.orientation == 0:
                cur_y += 1
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = ["0" * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n {i+1} |" + " | ".join(row) + " | "

        if self.hid:
            res = res.replace("◙", "0")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x+dx, d.y+dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "◙"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shoot(self, d):
        if self.out(d):
            raise BoardOutException()

        if self.busy:
            raise BoardWrongShipException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Корабль ранен")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1}{d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Введите координаты выстрела: ").split()

            if len(cords) != 2:
                print("Введите две координаты! ")
                continue

            x, y = cords

            if not(x.isdigit()) or (y.isdigit()):
                print("Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:

    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.user = User(player, computer)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def hello(self):
        print("Приветствуем вас в игре Морской бой!\n")
        print("Вводите координаты X и Y(через пробел)\n")
        print("X - номер строки, Y - номер столбца\n")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя: \n")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера: \n")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь")
                repeat = self.user.move()
            else:
                print("Ходит компьютер")
                repeat = self.ai.move()
            if repeat:
                num += 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Выиграл игрок!")
                break

            if self.user.board.count == 7:
                print("-" * 20)
                print("Выиграл компьютер!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()