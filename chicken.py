import random
import numpy as np

min_bet = 100
chicken_cost = 25
initial_wad = 35000
bet_mod = .01
initial_odds = 0.5
chickens = 0
num_chickens = 0
dict = {}
results_dict = {}
attempts = 0
best_session = [0,0]
lowest_attempts = [0,0,99999999999]
for bet_mod in np.arange(.4, .5, .1):
    success = 0
    failure = 0
    attempts = 0
    for i in range(1000):
        wad = initial_wad
        chickens = 0
        chicken_wins = 0
        bet = min_bet
        while wad > 0 and wad < 100000000:
            wad -= chicken_cost
            chicken = True
            num_chickens += 1
            bet = min_bet
            odds = initial_odds
            while chicken:
                wad -= bet
                outcome = random.random()
                if outcome <= odds:
                    if odds < .7:
                        odds += .01
                    wad += 2 * bet
                    chicken_wins += 1
                    new_bet = (wad * (odds-.5 + .02) * 2)
                    bet = new_bet if new_bet > min_bet else min_bet
                else:
                    chicken = False
                    if chicken_wins not in dict:
                        dict[chicken_wins] = 1
                    else:
                        dict[chicken_wins] += 1
                attempts += 1

        if wad <= 0:
            failure += 1
        if wad >= 100000000:
            success += 1

    results_dict[round(bet_mod, 2)] = [success, attempts/1000]
    # if success > best_session[0]:
    #     best_session = [success, bet_mod, attempts/1000]
    # if attempts/1000 < lowest_attempts[2]:
    #     lowest_attempts = [success, bet_mod, attempts/1000]


print(results_dict)
