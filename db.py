import random
from problem import Problem
from paper import Paper

class DB:
    def __init__(self):
        self.problem_db = []

    def generate_fake(self, paper):
        for i in range(3000):
            model = Problem()
            model.id = i
            model.difficulty = random.random()
            if i < 1001:
                model.type = 1
                model.score = paper.each_type_score[model.type-1] / \
                        paper.each_type_count[model.type-1]
            if i > 1000 and i < 2001:
                model.type = 2
                model.score = paper.each_type_score[model.type-1] / \
                        paper.each_type_count[model.type-1]
            if i > 2000 and i < 3001:
                model.type = 3
                model.score = paper.each_type_score[model.type-1] / \
                        paper.each_type_count[model.type-1]
            points = []
            # count = random.randint(1, 2)
            count = 1
            for j in range(count):
                points.append(random.randint(1, 10))
            model.points = points
            self.problem_db.append(model)

    def create_from_problem_list(self, problem_list):
        self.problem_db = problem_list
