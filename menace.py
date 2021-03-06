import numpy as np
import itertools
import pickle
import tictactoe
import pygame
import time
from pygame.locals import *
import sys
from tqdm import tqdm

# https://raw.githubusercontent.com/nyergler/teaching-python-with-pygame/master/ttt-tutorial/tictactoe.py
class State():
    def __init__(self, state):
        self.state = state
        self.beads = self.init_beads()
    
    def init_beads(self):
        beads = {}
        zero_count = max(self.state.count('0') - 1,2)
        for idx, i in enumerate(self.state):
            if i == '0':
                beads[idx] = zero_count
        return beads
    
    def get_beads(self):
        rand = np.random.rand(1)
        values = np.array(list(self.beads.values()))
        keys = np.array(list(self.beads.keys()))
        if np.sum(values) == 0:
            values = np.ones(values.shape[0])
        values = values / np.sum(values)
        #print(values)
        prob = 0
        for  idx, i in enumerate(values):
            prob += i
            if rand < prob:
                return keys[idx]
        
    def set_beads(self, key, reward):
        self.beads[key] += reward

def create_states(all_permutations):
    states = {}
    for string in all_permutations:
        states[string] = State(string)
    return states

def check_win_case(i,j,k, state):
    if(state[i] == state[j] and state[i] == state[k] and state[i] != '0'):
        return True
    return False
def check_win(state):
    if check_win_case(0,4,8, state):
        return True
    elif check_win_case(0,1,2,state):
        return True
    elif check_win_case(0,3,6,state):
        return True
    elif check_win_case(1,4,7,state):
        return True
    elif check_win_case(2,4,6,state):
        return True
    elif check_win_case(2,5,8,state):
        return True
    elif check_win_case(3,4,5,state):
        return True
    elif check_win_case(6,7,8,state):
        return True
    else:
        return False

def check_draw(states):
    if states.count('0') == 0:
        return True
    return False

def give_reward(states, menacing_states, menacing_steps, reward):
    for idx, state in enumerate(menacing_states):
        #print(''.join(list(state)))
        #print(menacing_steps[idx], idx)
        #print(states[''.join(list(state))].beads)
        states[''.join(list(state))].set_beads(menacing_steps[idx], reward)
        #print(states[''.join(list(state))].beads)

def prnt_game(state):
    """
    for idx, i in enumerate(state):
        print(i + ' | ', end='')
        if (idx+1)%3 == 0:
            print('\n- | - | -')
    """
    pass
        
def quit_prompt():
    print('Wanna Quit? Press Y')
    s = input()
    if s == 'Y':
        return True
    return False

def check_state(states, current_state):
    if ''.join(current_state) in states:
        return states
    states[''.join(current_state)] = State(current_state)
    return states

def game_on(states, path):
    try:
        pickle_in = open(path,"rb")
        states = pickle.load(pickle_in)
        print('Model Loaded')
    except FileNotFoundError:
        pass
    #print(states['000000001'].beads)
    wanna_quit = False
    while(not wanna_quit):
        print("Game Start")
        current_state = list('000000000')
        prnt_game(current_state)
        menacing_steps = []
        menacing_states = []
        pygame.init()
        tictactoe.grid = [ [ None, None, None ], \
                            [ None, None, None ], \
                            [ None, None, None ] ]
        tictactoe.winner = None
        ttt = pygame.display.set_mode ((300, 325))
        pygame.display.set_caption ('Tic-Tac-Toe')
        board = tictactoe.initBoard (ttt)
        new_game = False
        while(not new_game):
            try:
                for event in pygame.event.get():
                    if event.type is QUIT:
                        wanna_quit = True
                        new_game = True
                        break
                    elif event.type is MOUSEBUTTONDOWN:
                        # the user clicked; place an X or O
                        board, row, col = tictactoe.clickBoard(board)
                        # check for a winner
                        tictactoe.gameWon(board)
                        tictactoe.showBoard(ttt, board)
                        if row is None:
                            continue
                        a = row * 3 + col
                        if current_state[a] == '0':
                            current_state[a] = '1'
                            states = check_state(states, current_state)
                        else:
                            print('The place is already  filled! Please fill an unoccupied  place')
                            continue
                        if check_win(current_state):
                            give_reward(states, menacing_states, menacing_steps, -1)
                            prnt_game(current_state)
                            print('User won')
                            # wanna_quit = quit_prompt()
                            time.sleep(1)
                            new_game = True
                            break
                        if check_draw(current_state):
                            give_reward(states, menacing_states, menacing_steps, 1)
                            prnt_game(current_state)
                            print('Game Draw')
                            # wanna_quit = quit_prompt()
                            time.sleep(1)
                            new_game = True
                            break
                        #print('********')
                        #print(''.join(current_state))
                        menacing_states.append(tuple(current_state))
                        current_bead = states[''.join(current_state)].get_beads()
                        menacing_steps.append(current_bead)
                        #print(current_bead)
                        #print('********')
                        row_bead = int(current_bead / 3)
                        col_bead = current_bead % 3
                        tictactoe.drawMove (board, row_bead, col_bead, "O")
                        tictactoe.gameWon(board)
                        tictactoe.showBoard(ttt, board)
                        if current_state[current_bead] == '0':
                            current_state[current_bead] = '2'
                            states = check_state(states, current_state)
                        else:
                            print('The place is already filled! Please fill an unoccupied place')
                            break
                        if check_win(current_state):
                            give_reward(states, menacing_states, menacing_steps, 3)
                            prnt_game(current_state)
                            print('Menace won')
                            # wanna_quit = quit_prompt()
                            time.sleep(1)
                            new_game = True
                            break
                        if check_draw(current_state):
                            give_reward(states, menacing_states, menacing_steps, 1)
                            prnt_game(current_state)
                            print('Game Draw')
                            # wanna_quit = quit_prompt()
                            time.sleep(1)
                            break
                        prnt_game(current_state)
                        tictactoe.showBoard(ttt, board)
                    tictactoe.showBoard(ttt, board)
            except ValueError:
                print('The place is already  filled! Please fill an unoccupied  place')
                continue
def train_game(states, path, iterations):
    
    for _ in tqdm(range(iterations)):
        #print("Game Start")
        current_state = list('000000000')
        prnt_game(current_state)
        menacing_steps1 = []
        menacing_states1 = []
        menacing_steps2 = []
        menacing_states2 = []
        while(True):
            try:
                #print('PLAYER 1')
                menacing_states1.append(tuple(current_state))
                current_bead = states[''.join(current_state)].get_beads()
                menacing_steps1.append(current_bead)
                current_state[current_bead] = '1'
                states = check_state(states, current_state)
                #print(current_bead)
                #prnt_game(current_state) 
                if check_win(current_state):
                    #print('One won')
                    give_reward(states, menacing_states1, menacing_steps1, 3)
                    give_reward(states, menacing_states2, menacing_steps2, -1)
                    prnt_game(current_state) 
                    break
                if check_draw(current_state):
                    #print('Game Draw')
                    give_reward(states, menacing_states1, menacing_steps1, 1)
                    give_reward(states, menacing_states2, menacing_steps2, 1)
                    prnt_game(current_state)
                    break
                #print('PLAYER 2')
                #print(''.join(current_state))
                menacing_states2.append(tuple(current_state))
                current_bead = states[''.join(current_state)].get_beads()
                menacing_steps2.append(current_bead)
                current_state[current_bead] = '2'
                states = check_state(states, current_state)
                #print(current_bead)
                #prnt_game(current_state) 
                if check_win(current_state):
                    #print('Two won')
                    give_reward(states, menacing_states1, menacing_steps1, -1)
                    give_reward(states, menacing_states2, menacing_steps2, 3)
                    prnt_game(current_state)
                    break
                if check_draw(current_state):
                    #print('Game Draw')
                    give_reward(states, menacing_states1, menacing_steps1, 1)
                    give_reward(states, menacing_states2, menacing_steps2, 1)
                    prnt_game(current_state)
                    break
                #prnt_game(current_state)
            except ValueError:
                print('The place is already  filled! Please fill an unoccupied  place')
                continue
    print('training completed')
    pickle_out = open(path,"wb")
    pickle.dump(states, pickle_out)
    pickle_out.close()

def main():
    argv = sys.argv
    if len(argv) == 3:
        mode = argv[1]
        iterations = int(argv[2] )
    elif len(argv) == 2:
        mode = argv[1]
        iterations = 10000
    else:
        mode =  'test'
    path = 'model.pickle'
    states = {'000000000' : State('000000000')}
    if mode=='test':
        game_on(states, path)
    else:
        print('Training started')
        train_game(states, path, iterations)

if __name__ == "__main__":
    main()
    pass