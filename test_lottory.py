from cogs import lottory
import multiprocessing
import timeit
import itertools
import numpy as np
import random

payout_table = {True:{0:2000, 1:2000, 2:10000, 3:250000, 4:50000000},
                False:{0:0, 1:0, 2:0, 3:20000, 4:2000000}}



number_of_tickets = 10000000
number_of_processes = 10
per_process = int(number_of_tickets / number_of_processes)
numbers = [x for x in range(1,24)]
all_the_combs = list(itertools.combinations(numbers, 4))
inputs = [per_process] * number_of_processes

def quickpick4(input):
    number_of_tickets = input
    return map(lambda x: combinations_list[x], [random.randint(0,len(all_the_combs)-1) for i in range(number_of_tickets)])

def mp_handler(number_of_tickets):
    p = multiprocessing.Pool(number_of_processes)
    p.map(mp_worker, inputs)

def mp_worker(input):
    ticket_list = quickpick4(input)

start = timeit.default_timer()

if __name__ == '__main__':
    mp_handler()

stop = timeit.default_timer()

print ("Process took: ", stop - start, "seconds")
