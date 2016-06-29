# -*- coding: utf-8 -*-

import time
from random import randint, random
from db import DB
from paper import Paper
from unit import Unit

FKPCOV = 0.5 # 知识点覆盖率权重
FDIFF = 0.5 # 试卷难度权重
POPULATION_NUM = 100 # 种群个体数
SELECT_NUM = 30 # 自然选择后的种群个体数


def is_contain_points(paper, problem):
    """
    返回试题包含的知识点是否在试卷要求的知识点中
    """

    for i in range(len(problem.points)):
        if problem.points[i] in paper.points:
            return True

    return False


def set_kp_coverage(unit_list, paper):
    """
    计算知识点覆盖率
    """

    for i in range(len(unit_list)):
        each_point_score = [0] * 100
        for p in unit_list[i].problem_list:
            for point in p.points:
                each_point_score[point] += p.score

        result = 0

        for j in range(len(paper.points)):
            result += (1 - abs(each_point_score[paper.points[j]]
                               - paper.each_point_score[j])
                       * 1.00
                       / paper.each_point_score[j])

        unit_list[i].kp_coverage = result * 1.00 / len(paper.points)

    return unit_list


def set_adaptation_degree(unit_list, paper, FKPCOV, FDIFF):
    """
    计算种群的适应度
    """

    set_kp_coverage(unit_list, paper)
    for i in range(len(unit_list)):
        unit_list[i].adaptation_degree = 1 - (1 - unit_list[i].kp_coverage) \
                * FKPCOV - abs(unit_list[i].difficulty - paper.difficulty) \
                * FDIFF

    return unit_list


def generate_one_unit(i, paper, problem_list):
    """
    随机生成一个个体
    """

    unit = Unit()
    unit.id = i + 1

    each_type_count = paper.each_type_count
    print problem_list
    while paper.total_score != unit.sum_score:
        unit.problem_list = []
        for j in range(len(each_type_count)):
            one_type_problem = [
                p for p in problem_list
                if p.type == j+1 and is_contain_points(p, paper)]

            for k in range(0, each_type_count[j]):
                length = len(one_type_problem)
                index = randint(0, length - k - 1)
                unit.problem_list.append(one_type_problem[index])
                one_type_problem[index], one_type_problem[length-k-1] = \
                    one_type_problem[length-k-1], \
                    one_type_problem[index]

    return unit


def generate_unit_list(count, paper, problem_list):
    """
    随机生成一个种群
    """

    unit_list = []
    for i in range(count):
        unit = generate_one_unit(i, paper, problem_list)
        unit_list.append(unit)

    return unit_list


def initial_population(count, paper, problem_list):
    """
    生成初始种群
    """

    unit_list = generate_unit_list(count, paper, problem_list)
    set_kp_coverage(unit_list, paper)
    set_adaptation_degree(unit_list, paper, FKPCOV, FDIFF)

    return unit_list


def roulette(unit_list, count):
    """
    轮盘赌算法实现自然选择过程
    """

    selected_unit_list = []
    all_adaptation_degree = 0
    for u in unit_list:
        all_adaptation_degree += u.adaptation_degree

    while len(selected_unit_list) != count:
        degree = 0.0
        rand_degree = randint(1, 100) * 0.01 * all_adaptation_degree

        for j in range(len(unit_list)):
            degree += unit_list[j].adaptation_degree
            if degree >= rand_degree:
                if not unit_list[j] in selected_unit_list:
                    selected_unit_list.append(unit_list[j])

                break

    return selected_unit_list


def pick_best(unit_list):
    """
    每次选择保留最优个体
    """

    best_unit = max(unit_list, key=lambda u: u.adaptation_degree)
    return best_unit


def select(unit_list, count):
    """
    返回自然选择后的种群
    """

    selected_unit_list = []
    selected_unit_list += roulette(unit_list, count - 1)
    selected_unit_list.append(pick_best(unit_list))
    return selected_unit_list


def cross(unit_list, count, paper):
    """
    基因重组
    """

    crossed_unit_list = []
    while (len(crossed_unit_list) != count):
        index_one = randint(0, len(unit_list) - 1)
        index_two = randint(0, len(unit_list) - 1)
        if index_one == index_two:
            continue

        unit_one = unit_list[index_one]
        unit_two = unit_list[index_two]
        cross_position = randint(0, unit_one.problem_count - 2)
        score_one = unit_one.problem_list[cross_position].score + \
            unit_one.problem_list[cross_position+1].score
        score_two = unit_two.problem_list[cross_position].score + \
            unit_two.problem_list[cross_position+1].score

        if score_one == score_two:
            unit_new_one = Unit()
            unit_new_one.problem_list += unit_one.problem_list
            unit_new_two = Unit()
            unit_new_two.problem_list += unit_two.problem_list
            p = random()
            if p < 0.8:
                for i in range(cross_position, cross_position + 2):
                    unit_new_one.problem_list[i] = unit_two.problem_list[i]
                    unit_new_two.problem_list[i] = unit_one.problem_list[i]

            unit_new_one.id = len(crossed_unit_list)
            unit_new_two.id = unit_new_one.id + 1
            if len(crossed_unit_list) < count:
                crossed_unit_list.append(unit_new_one)

            if len(crossed_unit_list) < count:
                crossed_unit_list.append(unit_new_two)

        crossed_unit_list = list(set(crossed_unit_list))

    set_kp_coverage(crossed_unit_list, paper)
    set_adaptation_degree(crossed_unit_list, paper, FKPCOV, FDIFF)
    return crossed_unit_list


def change(unit_list, problem_list, paper):
    """
    变异
    """

    index = 0
    for u in unit_list:
        p = random()
        if p < 0.1:
            index = randint(0, len(u.problem_list) - 1)
            temp = u.problem_list[index]
            small_db = [
                prob for prob in problem_list
                if is_contain_points(paper, prob) and prob.score == temp.score
                and prob.type == temp.type and prob.id != temp.id]

            if len(small_db) > 0:
                change_index = randint(0, len(small_db) - 1)
                u.problem_list[index] = small_db[change_index]

    set_kp_coverage(unit_list, paper)
    set_adaptation_degree(unit_list, paper, FKPCOV, FDIFF)
    return unit_list


def is_end(unit_list, end_condition):
    if unit_list is not None:
        for i in range(len(unit_list)):
            if (unit_list[i].adaptation_degree >= end_condition):
                return True

    return False


def show_result(unit_list, expand):
    result = [u for u in unit_list if u.adaptation_degree >= expand]
    for u in result:
        print u"第 %d 套" % u.id
        print u"题目数量\t知识点分布\t难度系数\t适应度"
        print u"%d\t\t%.2f\t\t%.2f\t\t%.2f" % (
            u.problem_count, u.kp_coverage,
            u.difficulty, u.adaptation_degree)


def show_unit(unit_list):
    for u in unit_list:
        print u"试卷编号\t知识点分布\t难度系数\t适应度"
        print u"%d\t\t%.2f\t\t%.2f\t\t%.2f" % (
                u.id, u.kp_coverage, u.difficulty, u.adaptation_degree)


def show_opt_unit(unit_list):
    opt_unit = max(unit_list, key=lambda u: u.adaptation_degree)

    print u"第 %d 套" % opt_unit.id
    print u"题目数量\t知识点分布\t难度系数\t适应度"
    print u"%d\t\t%.2f\t\t%.2f\t\t%.2f" % (
        opt_unit.problem_count, opt_unit.kp_coverage,
        opt_unit.difficulty, opt_unit.adaptation_degree)
    print
    """
    print u"知识点覆盖率：", opt_unit.kp_coverage
    print u"难度：", opt_unit.difficulty
    print u"最大适应值：", opt_unit.adaptation_degree
    """


class Genetic:
    def __init__(self, paper, db):
        self.paper = paper
        self.db = db

    def run(self, expand):
        count = 1
        run_count = 500
        unit_list = initial_population(POPULATION_NUM,
                                       self.paper,
                                       self.db.problem_db)

        while (not is_end(unit_list, expand)):
            count = count + 1
            if (count > run_count):
                break
            unit_list = select(unit_list, SELECT_NUM)
            unit_list = cross(unit_list, POPULATION_NUM, self.paper)
            if (is_end(unit_list, expand)):
                break

            unit_list = change(unit_list, self.db.problem_db, self.paper)
            print u"第 %d 代：" % (count-1)
            show_opt_unit(unit_list)

        if (count <= run_count):
            print u"在第 %d 代得到结果" % count
            print u"期望试卷难度：" + str(self.paper.difficulty)
            show_result(unit_list, expand)
            for u in unit_list:
                if u.adaptation_degree >= expand:
                    return u

    def test_run(self):
        count = 1
        expand = 0.98
        run_count = 500

        while True:
            count = 1
            unit_list = initial_population(POPULATION_NUM,
                                           self.paper,
                                           self.db.problem_db)

            print u"初始种群:"
            show_unit(unit_list)
            print u"----------迭代开始-----------"

            while (not is_end(unit_list, expand)):
                print u"在第 %d 代未得到结果" % count
                show_opt_unit(unit_list)
                count = count + 1
                if (count > run_count):
                    print u"失败，请重新设计条件"
                    break

                unit_list = select(unit_list, SELECT_NUM)
                unit_list = cross(unit_list, POPULATION_NUM, self.paper)

                if (is_end(unit_list, expand)):
                    break

                unit_list = change(unit_list, self.db.problem_db, self.paper)

            if (count <= run_count):
                print u"在第 %d 代得到结果" % count
                print u"期望试卷难度：" + str(self.paper.difficulty)
                show_result(unit_list, expand)
                break


def main():
    paper = Paper()

    paper.id = 1
    paper.total_score = 100
    paper.difficulty = 0.72
    paper.points = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    paper.each_point_score = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    paper.each_type_count = [15, 15, 5]
    paper.each_type_score = [30, 30, 40]

    db = DB()
    db.generate_fake(paper)
    genetic = Genetic(paper, db)
    start = time.clock()
    genetic.test_run()
    end = time.clock()
    print u"总共用时：", end - start, " 秒"


if __name__ == '__main__':
    main()
