from random import randint


class FieldException(Exception):
    pass


class FieldOutException(FieldException):
    def __str__(self):
        return "Вы стреляете за пределы поля"


class FieldUsedException(FieldException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку :/"


class FieldWrongShipException(FieldException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"{self.x}, {self.y}"


class Ship:
    def __init__(self, bow, n, o):
        self.bow = bow
        self.n = n
        self.o = o
        self.lives = n

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.n):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Field:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, 1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise FieldWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise FieldOutException()

        if d in self.busy:
            raise FieldUsedException

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Есть пробитие!")
                    return True
        self.field[d.x][d.y] = "."
        print("Промах!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except FieldException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход ПК: {d.x + 1}, {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            move = input("Сделайте ход: ").split()
            if len(move) != 2:
                print("Необходимо ввести 2 координаты!")
                continue

            x, y = move

            if not (x.isdigit()) or not (y.isdigit()):
                print("Вы ввели не числа ;)")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        pc = self.random_board()
        pc.hid = True

        self.ai = AI(pc, player)
        self.us = User(player, pc)

    def try_board(self):
        boats = [3, 2, 2, 1, 1, 1, 1]
        board = Field(size=self.size)
        trying = 0
        for b in boats:
            while True:
                trying += 1
                if trying > 100:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), b, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except FieldWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("-" * 40)
        print("Добро пожаловать в игру Sea Battle!")
        print("-" * 40)
        print("Управление: ")
        print("Чтобы сделать ход, введите координаты клетки в формате: x y ")
        print("где x - номер строки, y - номер столбца")
        print("-" * 40)
        print("Желаю Вам удачи! =)")
        print("-" * 40)

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваша доска: ")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера: ")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Вы выиграли! Молодец!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл! Не расстраивайтесь, вы молодец!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()