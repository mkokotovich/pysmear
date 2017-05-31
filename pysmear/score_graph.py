import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cycler import cycler

class ScoreGraphManager():
    def __init__(self, score_to_play_to):
        self.scores = {}
        self.score_to_play_to = score_to_play_to
        self.label_constants = {
                11:[ 15, 7 ],
                15:[ 20, 10],
                21:[ 25, 10]
                }
        self.colors= [
                "blue",
                "orange",
                "plum",
                "sienna",
                "khaki",
                "linen",
                "cyan",
                "green"
                ]


    def reset(self):
        self.scores = {}


    def add_new_hand_to_scores(self, game_id, current_scores):
        if game_id not in self.scores.keys():
            self.scores[game_id] = [ [x] for x in current_scores ] 
        else:
            for i in range(0, len(current_scores)):
                self.scores[game_id][i].append(current_scores[i])
        return self.scores[game_id]


    def remove_game_from_scores(self, game_id):
        del self.scores[game_id]


    def export_graph(self, game_id, filename, current_scores, player_names):
        scores_so_far = self.add_new_hand_to_scores(game_id, current_scores)

        # Generate X-axis data
        hands = range(0, len(scores_so_far[0]))

        plt.rc('axes', prop_cycle=(cycler('color', self.colors)))

        # For each player, plot a line of their scores
        for i in range(0, len(scores_so_far)):
            plt.plot(hands, scores_so_far[i], label=player_names[i])


        # Add a legend of the player names
        plt.legend(loc='upper left')

        # Set graph details
        ax = plt.gca()
        ax.set_ylim([0, self.label_constants[self.score_to_play_to][0]])
        ax.set_ylabel("Points")
        x_tick_max=max(self.label_constants[self.score_to_play_to][1], len(scores_so_far[0]) + 1)
        ax.set_xticks(range(0, x_tick_max))
        ax.set_xlabel("Hand")

        # Save graph to file
        plt.savefig(filename)

        # Close graph
        plt.close()
