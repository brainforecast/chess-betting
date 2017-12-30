import numpy as np
import time
import gc

#gc.enable()

def initialize_array(players):
	np.zeros(n,n)

def calc_wins_expected(player_A_Elo,player_B_Elo,players,sims): #numpy 
	win_without_draws = np.divide(1,1+np.float_power(10,(player_B_Elo-player_A_Elo)/400))
	draw = np.full((1,players**2*sims),0.65)
	win = (1-draw)*win_without_draws
	loss = 1 - win - draw
	return([win,draw,loss]) #array of np arrays

def simulate_double_round(player_A_Elo,player_B_Elo,random_seed_1,random_seed_2,players,sims):
	wins_expected = calc_wins_expected(player_A_Elo,player_B_Elo,players,sims)
	win_tiled = wins_expected[0]
	draw_tiled = wins_expected[1]
	win_only = np.where(random_seed_1 <= win_tiled,0.5,0) #for tiebreak optimization
	draw_only = np.where(random_seed_1 < win_tiled + draw_tiled,0.5,0)
	#lose_only = np.where(random_seed_1 >= (win_tiled + draw_tiled), -0.01, 0)
	win_only_2 = np.where(random_seed_2 <= win_tiled,0.5,0) #for tiebreak optimization
	draw_only_2 = np.where(random_seed_2 < win_tiled + draw_tiled,0.5,0) 
	#lose_only_2 = np.where(random_seed_2 >= (win_tiled + draw_tiled), -0.01, 0)
	result = draw_only + win_only + draw_only_2 + win_only_2 #+ lose_only + lose_only_2
	return(result)

sims = 100000
candidates = ("Karjakin", "Aronian", "Ding", "Mamedyarov", "Grischuk", "Caruana", "So", "Kramnik")
players = len(candidates)
tic = time.time()
A = np.array([2760,2801,2774,2799,2782,2799,2788,2787]) #Put player Elo here!
A_repeat = np.repeat(A,players*sims)
B = np.tile(A,players*sims)
random_seed_1 = np.random.random(players**2*sims) #[0,1)
random_seed_2 = np.random.random(players**2*sims)
long_results = simulate_double_round(A_repeat,B,random_seed_1,random_seed_2,players,sims)
test_range = np.arange(players**2)
tri_upper = np.where((test_range % players) > np.floor((test_range / players)),1,0)
tri_upper_mask = np.tile(tri_upper,sims)
x = np.multiply(long_results,tri_upper_mask)
mirror = 2 - x
y = np.multiply(mirror,tri_upper_mask)
x.shape = (players,players,sims)
y.shape = (players,players,sims)
x = np.transpose(x,(2,0,1))
y = np.transpose(y,(2,1,0))
wins = np.sum(x+y,axis=2)
winmax = np.amax(wins,axis=1)
winmax.shape = (sims,1)
winner_with_ties = np.where(winmax == wins,1,0)
winner_with_EV_ties = np.sum(winner_with_ties,axis=1)
winner_with_EV_ties.shape = (sims,1)
winner_split_ties = winner_with_ties/winner_with_EV_ties
#print(winner_split_ties)
end_result = np.sum(winner_split_ties,axis=0)
#print(end_result)
percent_win_per_player = end_result/np.sum(end_result)*100
toc = time.time()
i = 0
for name in candidates:
	print(name, percent_win_per_player[i])
	i += 1
print("Time taken: {}s".format(toc-tic))