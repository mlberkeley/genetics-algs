
# TODO ugly hack to appease Roy's laptop
import matplotlib
matplotlib.use("Qt4Agg")

import matplotlib.pyplot as plt

from random import random

import numpy as np
from PIL import Image
import moviepy.editor as mpy

from data import Data
from evaluator import Evaluator
from mutations import Mutations
from tree_methods import TreeMethods

class Algorithm(object):
    @staticmethod
    def make_function(data, node_var):
        """ Generates a function.

            Args:
                data: Data object
                node_var: label for variable we are interested in

            Returns:
                sympy Function
        """
        TREE_COUNT = 10
        GENERATIONS = 100
        PROB_REPRODUCTION = 0.5
        PROB_POINT = 0.5
        #PROB_CROSSOVER = 0.1
        PROB_CROSSOVER = 0

        THRESHOLD = -1e-5

        # Generate a pool of trees
        # TODO what if create_grow_tree gives us a + node as a leaf?
        trees = [TreeMethods.create_grow_tree(500) for _ in range(TREE_COUNT)]

        # For animation
        gif_fnames = []

        best_fitnesses = []

        for i in range(GENERATIONS):
            print("Generation: {0}".format(i))
            # Draw pool
            gif_fname = "temp/_iteration_{0}.png".format(i)
            gif_fnames.append(gif_fname)
            Algorithm.draw_pool(trees, gif_fname)

            new_trees = []

            fitnesses = []
            for tree in trees:
                fitness = Evaluator.score(tree, data, node_var)
                fitnesses.append(fitness)
            fitnesses = np.array(fitnesses)

            # Save best fitness
            best_fitnesses.append(np.max(fitnesses))

            # If a fitness is super good just end the algorithm
            if np.max(fitnesses) > THRESHOLD:
                print("Threshold reached! Ending.")
                break

            # Translate and normalize fitnesses until they form a
            # probability distribution
            #fitnesses += -np.min(fitnesses) + 1e-5
            #fitnesses /= np.sum(fitnesses)

            # TODO change this
            # Use an extremely nonlinear probability function
            fitnesses *= -1
            fitnesses += 1e-5
            fitnesses = 1/fitnesses
            fitnesses /= np.sum(fitnesses)

            while len(new_trees) <= TREE_COUNT:
                r = random()
                if r < PROB_POINT:
                    # Point mutation
                    candidate_tree = np.random.choice(trees, 1, p=fitnesses)[0]
                    tree = Mutations.mutate_point(candidate_tree)
                    new_trees.append(tree)
                elif r < PROB_POINT + PROB_CROSSOVER:
                    # Crossover mutation
                    [ctree1, ctree2] = np.random.choice(trees, 2, p=fitnesses)
                    if len(ctree1.children) == 0 or len(ctree2.children) == 0:
                        # TODO handle this case somehow
                        # Abort, we dun goofed
                        continue
                    tree1, tree2 = Mutations.mutate_crossover(ctree1, ctree2)
                    new_trees.append(tree1)
                    new_trees.append(tree2)
                else:
                    # Reproduction mutation
                    candidate_tree = np.random.choice(trees, 1, p=fitnesses)[0]
                    tree = candidate_tree.deepcopy()
                    new_trees.append(tree)

            trees = new_trees

        # Plot fitnesses
        fig, ax = plt.subplots()
        ax.set_title("Fitness vs. Iterations")
        ax.set_xlabel("Iterations")
        ax.set_ylabel("Fitness")
        ax.plot(best_fitnesses)
        fig.savefig("demo/fitness.png")

        # Animate pool
        animation = mpy.ImageSequenceClip(gif_fnames, fps=1)
        animation.write_gif("demo/animation.gif", fps=1)

        # Return trees
        scores = [Evaluator.score(tree, data, node_var) for tree in trees]
        best_tree = trees[np.argmax(scores)]
        return best_tree.collapse()

    @staticmethod
    def draw_pool(pool, fname):
        # TODO move this method?
        """ Draws a list of trees.

            Args:
                pool: list of trees
                fname: filename to save image to
        """
        fnames = []
        for i, tree in enumerate(pool):
            f = "temp/_temp_{0}.png".format(i)
            tree.ete_draw(f)
            fnames.append(f)

        # Stolen from StackOverflow
        images = [Image.open(f) for f in fnames]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)
        
        new_im = Image.new('RGB', (total_width, max_height), "white")
        
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]
        
        new_im.save(fname)

if __name__ == "__main__":
    data = Data("pendulum.pkl")
    #data = Data("const.pkl")
    #data = Data("linear.pkl")
    print(Algorithm.make_function(data, "x"))
