import random
from problem import Problem

class DB:
    def __init__(self):
        self.problem_db = []
        for i in range(5000):
            model = Problem()
            model.id = i
            model.difficulty = random.uniform(0.3, 1)
            if i < 1001:
                model.type = 1
                model.score = 1
            if i > 1000 and i < 2001:
                model.type = 2
                model.score = 2
            if i > 2000 and i < 3001:
                model.type = 3
                model.score = 2
            if i > 3000 and i < 4001:
                model.type = 4
                model.score = 2
            if i > 4000 and i < 5001:
                model.type = 5
                model.score = 5
            points = []
            count = random.randint(1, 5)
            for j in range(count):
                points.append(random.randint(1, 100))
            model.points = points
            self.problem_db.append(model)
