from multiprocessing import Pool, Pipe
import numpy as np
import time
import sys

dict = {}
num_list = [x for x in range(1,24)]

def quickpick1(number_of_tickets=1):
    '''Returns a number of QP tickets'''
    np.random.shuffle(num_list)
    numbers = num_list[:4]
    megaball = np.random.randint(1,12)
    numbers.append(megaball)
    return numbers

def parse_ticket(winner, ticket):
    match = [x for x in ticket[:4] if x in winner[:4]]
    mega = ticket[4] == winner[4]
    return len(match), mega

def add_result_to_dict(dict, match, mega):
    if mega not in dict:
        dict[mega] = {match: 0}
    if match not in dict[mega]:
        dict[mega][match] = 0
    dict[mega][match] += 1
    return dict

if __name__ == '__main__':

    number_of_tickets = 100000000
    winner = quickpick1()
    for _ in range(number_of_tickets):
        ticket = quickpick1()
        match, mega = parse_ticket(winner, ticket)
        add_result_to_dict(dict, match, mega)

    for mega, matches in dict.items():
        for match, totals in matches.items():
            dict[mega][match] = totals / number_of_tickets

    print(dict)
