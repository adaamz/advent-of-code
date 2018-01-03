"""
Abstract base class for advent of code puzzle solvers.

"""
from abc import ABC, abstractmethod
import json
import numpy as np
import re


class PuzzleSolver(ABC):
    def __init__(self, from_file=None, from_str=None):
        if not (from_file or from_str):
            raise ValueError('PuzzleSolver needs to be initialized from '
                             'either file or string.')
        elif from_file and from_str:
            raise ValueError('PuzzleSolver ambiguous initialization.')
        elif from_str:
            self.raw_puzzle_input = from_str
        else:
            with open(from_file) as f:
                self.raw_puzzle_input = f.read()

    @abstractmethod
    def solve(self):
        pass

    @property
    def puzzle_input(self):
        return self.raw_puzzle_input

    def chars(self):
        for c in self.raw_puzzle_input:
            yield c

    def lines(self, conversion=None):
        for line in self.raw_puzzle_input.strip().split('\n'):
            if not conversion:
                yield line
            else:
                yield conversion(line)

    def lines_search(self, pattern):
        prog = re.compile(pattern)
        for line in self.raw_puzzle_input.strip().split('\n'):
            m = prog.search(line)
            yield m

    def lines_split(self, split_str, conversion=None):
        for line in self.raw_puzzle_input.strip().split('\n'):
            if not conversion:
                yield line.split(split_str)
            else:
                yield [conversion(x) for x in line.split(split_str)]

    def as_json(self):
        return json.loads(self.raw_puzzle_input)

    def as_bool_numpy_array(self, false='.'):
        """Given a matrix of .'s and #'s, return a boolean numpy array."""
        m = []
        for line in self.lines():
            row = (np.fromstring(line, dtype='b') != ord(false)).astype('?')
            m.append(row)
        return np.array(m)
