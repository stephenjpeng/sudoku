#!/usr/bin/python3
import copy
import numpy as np
try:
    import src.constants as constants
    import src.utils as utils
except ModuleNotFoundError:
    import constants
    import utils


class SudokuSolver():

    def __init__(self, problem, renderer=None):
        self.problem = np.array(problem)
        self.renderer = renderer
        self.rows   = self.rows_from_numpy(self.problem)
        self.cols   = self.cols_from_numpy(self.problem)
        self.blocks = self.blocks_from_numpy(self.problem)
        self.iter = 0
        self.render = False

        self.variables = set([(i, j) for i in range(constants.ROWS) for j in range(constants.COLUMNS)])
        self.domains = {}
        for var in self.variables:
            self.domains[var] = self.assign_domain(*var)

    def solve(self, render=True):
        self.render = render
        self.search(self.domains.copy())
        if np.min(self.problem) < 0:
            return False
        return self.problem

    def assign(self, domains, x, val):
        if self.render and callable(self.renderer):
            self.renderer(*x, val)
        othervals = domains[x].difference(set([val]))
        self.problem[x[0]][x[1]] = val
        if all(self.eliminate(domains, *x, otherval) for otherval in othervals):
            return domains
        else:
            return False

    def eliminate(self, domains, row, col, val):
        x = (row, col)
        if val not in domains[x]:
            return domains
        domains[x].remove(val)
        if not len(domains[x]):
            return False
        if len(domains[x]) == 1:
            lastval = next(iter(domains[x]))
            if not all(self.eliminate(domains, *y, lastval) for y in self.get_arcs(x)):
                return False
        for block in self.get_blocks(x):
            val_opts = [y for y in block if val in domains[y]]
            if len(val_opts) == 0:
                return False
            elif len(val_opts) == 1:
                if not self.assign(domains, val_opts[0], val):
                    return False
        return domains

    def search(self, domains):
        self.iter += 1
        if domains is False:
            return False
        if all(len(domains[x]) == 1 for x in self.variables):
            self.assign_singletons(domains)
            return self.domains
        k, x = min((len(domains[x]), x) for x in self.variables if len(domains[x]) > 1)
        return( utils.some(
            self.search(
                self.assign(copy.deepcopy(domains), x, val)
            ) for val in domains[x]
        ))

    def assign_singletons(self, domains):
        for x in self.variables:
            if self.problem[x[0]][x[1]] < 0:
                domains = self.assign(domains, x, next(iter(domains[x])))

    def get_blocks(self, x):
        row, col = x
        return [
            [(x[0], i) for i in range(9)],
            [(i, x[0]) for i in range(9)],
            [((row // 3) * 3 + (i // 3), (col // 3) * 3 + (i % 3)) for i in range(9)]
        ]

    def get_arcs(self, x):
        row, col = x
        block = utils.idx_to_blockno(row, col)
        worklist = set([x])
        for i in range(9):
            blocki = ((row // 3) * 3 + (i // 3), (col // 3) * 3 + (i % 3)) 
            worklist.add((row, i))
            worklist.add((i, col))
            worklist.add(blocki)
        worklist.remove((row, col))
        return worklist

    ### utility functions ###

    def assign_domain(self, row, col):
        block = utils.idx_to_blockno(row, col)
        value = self.problem[row][col]
        if value != -1:
            return set([value])
        domain = set(list(range(1, 10)))
        domain = domain.difference(self.rows[row])
        domain = domain.difference(self.cols[col])
        domain = domain.difference(self.blocks[block])
        return domain

    def rows_from_numpy(self, board):
        rows = []
        for i in range(constants.ROWS):
            rows += [set(board[i, :])]
            rows[i].discard(-1)
        return rows

    def cols_from_numpy(self, board):
        cols = []
        for i in range(constants.COLUMNS):
            cols += [set(board[:, i])]
            cols[i].discard(-1)
        return cols

    def blocks_from_numpy(self, board):
        blocks = [] # ordered 0 1 2 / 3 4 5 / 6 7 8
        for i in range(constants.BLOCKS):
            row_lower, col_lower = utils.blockno_to_NW_idx(i)
            blocks += [set(board[row_lower:row_lower+3, col_lower:col_lower+3].flatten().tolist())]
            blocks[i].discard(-1)
        return blocks


if __name__=='__main__':
    # test_board = np.array([
        # [ 8,  5, -1, -1, -1,  2,  4, -1, -1],
        # [ 7,  2, -1, -1, -1, -1, -1, -1,  9],
        # [-1, -1,  4, -1, -1, -1, -1, -1, -1],
        # [-1, -1, -1,  1, -1,  7, -1, -1,  2],
        # [ 3, -1,  5, -1, -1, -1,  9, -1, -1],
        # [-1,  4, -1, -1, -1, -1, -1, -1, -1],
        # [-1, -1, -1, -1,  8, -1, -1,  7, -1],
        # [-1,  1,  7, -1, -1, -1, -1, -1, -1],
        # [-1, -1, -1, -1,  3,  6, -1,  4, -1],
    # ])
    test_board = np.array([
        [ 8,  5,  9,  6,  1,  2,  4,  3,  7],
        [ 8,  2,  3,  -1,  5,  4,  1,  6,  9],
        [ 1,  6,  4, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1,  1, -1,  7, -1, -1,  2],
        [ 3, -1,  5, -1, -1, -1,  9, -1, -1],
        [-1,  4, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1,  8, -1, -1,  7, -1],
        [-1,  1,  7, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1,  3,  6, -1,  4, -1],
    ])
    Solver = SudokuSolver(test_board)
    print(Solver.solve())
