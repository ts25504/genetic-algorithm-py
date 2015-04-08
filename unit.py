class Unit:
    def __init__(self):
        self.id = 0
        self.adaptation_degree = 0.00
        self.kp_coverage = 0.00
        self.problem_list = []
        self.__difficulty = 0.00
        self.__problem_count = 0
        self.__sum_score = 0

    @property
    def difficulty(self):
        diff = 0.00
        if self.sum_score == 0:
            return diff
        for p in self.problem_list:
            diff += (p.difficulty * p.score)
        self.__difficulty = diff / self.sum_score
        return self.__difficulty

    @property
    def problem_count(self):
        self.__problem_count = len(self.problem_list)
        return self.__problem_count

    @property
    def sum_score(self):
        self.__sum_score = 0
        for p in self.problem_list:
            self.__sum_score += p.score
        return self.__sum_score
