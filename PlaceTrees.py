#This code untilizes and code dowloaded from 
#       http://devmag.org.za/2009/05/03/poisson-disk-sampling/
#       for info on how this actually is working check
#       out the websight above their explination is
#       excelent. 
from math import log, sin, cos, sqrt, floor, ceil, pi
from random import random, randint, uniform
import csv, sys, copy

import pylab
from enhanced_grid import ListGrid2D

#----Random Queue----
class RandomQueue():
        ## pops elements randomly from queue
        def __init__(self,queue):               
                ## The internal list to store objects.
                self.queue = queue

        ##Returns True if this RandomQueue is empty.    
        def empty(self):
                return len(self.queue) <= 0
        
        ## Push a new element into the RandomQueue.
        def push(self, x):
                self.queue.append(x)
                
        def double(self):
                queue2 = copy.deepcopy(self.queue)
                return RandomQueue(queue2)
        
        # All elements can be selected equiprobably
        def pop(self):
                n = len(self.queue)
                
                if n <= 0:
                        raise IndexError('Cannot pop from emty container!')
                elif n == 1:
                        return self.queue.pop()
                else:
                        i = randint(0, n - 1)
                        j = n - 1
                        self.queue[i], self.queue[j] =  self.queue[j], self.queue[i]

                return self.queue.pop()

                
class PlaceTrees():
        def __init__(self,x,y,plotTrees):
                # ---create varables---
                
                #print 'PLACE TREES=============='
                #for line in plotTrees:
                #        print line
                #print '========================='
                
                SimAcers = x*y/4046.86 # calculates area of simulation in meters square and then converts to acres
                #for i in plotTrees:
                #        print i[6]
                        
                self.CrwnRadMax = max( [float(i[6]) for i in  plotTrees] )/2.  # maximum crown radius 
                #print "self.CrwnRadMax = ", self.CrwnRadMax
                # AllTrees list contains a list containing the index of a tree in plotTrees however many tiems that tree will apear in the sumulation
                #       Ex. if tree 12 from plotList appers 4 times in the simulation All trees will somewhere contain [12],[12],[12],[12]
                AllTrees = []
                for i in range(len(plotTrees)):
                        plotTrees[i].append([]) # append an empty list to the end of each list in plot trees 
                        for j in range( int( floor( plotTrees[i][8] * SimAcers )) ): 
                                AllTrees.append([i])
                self.AT = AllTrees
                self.plotTrees = plotTrees
                self.overlap = 0.05
                self.DistanceMatrix()
                self.x = x
                self.y = y
                

        
        def DistanceMatrix(self):
                plotTrees = self.plotTrees
                
                #compute distance Matrx using function r below
                TR = [] # tree radius distance matrix 
                for i in range(len(plotTrees)):
                        TR.append([])
                        for j in range(len(plotTrees)):
                                TR[i].append(self.r(plotTrees[i],plotTrees[j]))
                self.TR = TR
                
        
        def r(self,treeA,treeB):
                # If we took at two cone trees and draw a line from trunk to trunk then project this line verticaly uppward the
                # interseciton of the plane would look like the figure below. We should have two triangels. 
                #       /|\
                #      / | \
                #     /  |  \
                #    /   |   \        /|\  
                #   /    |    \      / | \
                #  /     |     \    /  |  \
                # /      |   a  \  / b |   \
                #/_______|_______\/____|<---\------- calc distance between trees here
                #        |       /     |     \
                #        |      /___c__|______\
                #        |             |
                #        |             |
                #------------------------
                # slicing each "tree" in half we can reduce the ploblem to two right triangles. Using a "similar trianges"
                # method we can caluate trainge b from trangle c. Then adding the legs of a and b and subtracting an allowed overlap ratio
                # we have the minimum distance from the frist tree to the second.
                
                pp = 1 - self.overlap
                htA = treeA[2]  # height
                cbhA = treeA[3] # crown base heiht
                crwnradA = treeA[6]/2. # crown radius
                htB = treeB[2]
                cbhB = treeB[3]
                crwnradB = treeB[6]/2.
                
                if cbhA == cbhB:
                        return pp*crwnradA + pp*crwnradB
                if cbhA > cbhB:
                        if htB <= cbhA:
                                return crwnradB
                        else:
                                return pp*crwnradA + pp*crwnradB*( (htB - cbhA)/(htB - cbhB) )
                        
                if cbhA < cbhB:
                        if htA <= cbhB:
                                return crwnradA
                        else:
                                return pp*crwnradB + pp*crwnradA*( (htA - cbhB)/(htA - cbhA) )
        """
        def rand_with_check(self):
                cell_size = self.CrwnRadMax/sqrt(2)
                inv_cell_size = 1. / cell_size
                grid = ListGrid2D(( int(ceil(self.x/cell_size)),int(ceil(self.y/cell_size)) ))
                tree_indexs = copy.deepcopy(self.AT) # create a copy of all trees so original is not modified
                
                ##@brief The square of the distance between the given points
                def sqr_dist((x0, y0), (x1, y1)):
                        return (x1 - x0)*(x1 - x0) + (y1 - y0)*(y1 - y0)
                
                def in_neighbourhood(p, r):
                                gp = grid_coordinates(p)
                                r_sqr = r*r
                                for cell in grid.square_iter(gp, 2):
                                        for q in cell:
                                                if sqr_dist(q, p) <= r_sqr:
                                                        return True
                                return False
                                
                def in_rectangle((x, y)):
                        return 0 <= x < self.x and 0 <= y < self.y
                
                for i in tree_indexs:
                        print
                        #set = False
                        #while set == False:
                                #p = (uniform(0, self.x),uniform(0, self.y))
                                #if in_rectangle(p) and not in_neighbourhood(p, r):
                                        #tree1.append(q)
                                        #out_rq.push(tree1)
                                        #grid[grid_coordinates(q)].append(q)
                                        #set = True
                
        """
        def variable_poisson(self):
                width = self.x
                height = self.y
                cell_size = self.CrwnRadMax/sqrt(2)
                inv_cell_size = 1. / cell_size
                k = 50
        
                ##@brief Returns a random integer in the range [0, n-1] inclusive.
                def rand(n):
                        return randint(0, n - 1)

                ##@brief The square of the distance between the given points
                def sqr_dist((x0, y0), (x1, y1)):
                        return (x1 - x0)*(x1 - x0) + (y1 - y0)*(y1 - y0)
                
                #Convert rectangle (the one to be sampled) coordinates to 
                # coordinates in the grid.
                def grid_coordinates((x, y)):
                        return (int(x*inv_cell_size), int(y*inv_cell_size))
                        
                # Generates a point randomly selected around
                # the given point, between r and 2*r units away.
                def generate_random_around((x, y), r):
                        rr = uniform(r, 3*r)
                        rt = uniform(0, 2*pi)
                        return rr*sin(rt) + x, rr*cos(rt) + y
                        
                # Is the given point in the rectangle to be sampled?
                def in_rectangle((x, y)):
                        return 0 <= x < width and 0 <= y < height
                
                def do_it():
                
                        def in_neighbourhood(p, r):
                                gp = grid_coordinates(p)
                                r_sqr = r*r
                                
                                for cell in grid.square_iter(gp, 2):
                                        for q in cell:
                                                if sqr_dist(q, p) <= r_sqr:
                                                        return True
                                return False
                
                        #Create the grid
                        treelist = copy.deepcopy(self.AT) # create a copy of all trees so original is not modified
                        grid = ListGrid2D(( int(ceil(width/cell_size)),int(ceil(height/cell_size)) ))
                        in_rq = RandomQueue(treelist)
                        
                        out_rq = RandomQueue([])
                        #generate the first point
                        tree1 = in_rq.pop()
                        p = (rand(width), rand(height))
                        tree1.append(p)
                        grid[grid_coordinates(p)].append(p)
                        out_rq.push(tree1)

                        #generate other points from points in queue.
                        while not in_rq.empty():
                                tree1 = in_rq.pop() # tree one index
                                t1ind = tree1[0]
                                out_rq_double = out_rq.double()
                                while not out_rq_double.empty():
                                        tree2 = out_rq_double.pop()
                                        p = tree2[1]
                                        t2ind = tree2[0] # tree two index
                                        r = self.TR[t1ind][t2ind]
                                        for i in range(k):                      
                                                q = generate_random_around(p, r)
                                                set = False
                                                if in_rectangle(q) and not in_neighbourhood(q, r):
                                                        tree1.append(q)
                                                        out_rq.push(tree1)
                                                        grid[grid_coordinates(q)].append(q)
                                                        set = True
                                                        break                                   
                                        if set == True: break
                                if set == False:
                                        self.overlap += .01
                                        self.DistanceMatrix()
                                        print ' overlap is now %s...' % self.overlap
                                        out_rq = do_it()
                        return out_rq
                
                out_rq = do_it()
                print ' successfully placed points with overlap = %s...' % self.overlap
                # append points from AllTrees to the empty list at the end of plotTrees
                for i in out_rq.queue:
                        self.plotTrees[i[0]][-1].append(i[1])
                
                return self.plotTrees
        def simple_random(self):
                width = self.x
                height = self.y
                cell_size = self.CrwnRadMax/sqrt(2)
                inv_cell_size = 1. / cell_size
                k = 50

                ##@brief Returns a random integer in the range [0, n-1] inclusive.
                def rand(n):
                        return randint(0, n - 1)

                ##@brief The square of the distance between the given points
                def sqr_dist((x0, y0), (x1, y1)):
                        return (x1 - x0)*(x1 - x0) + (y1 - y0)*(y1 - y0)
                
                #Convert rectangle (the one to be sampled) coordinates to 
                # coordinates in the grid.
                def grid_coordinates((x, y)):
                        return (int(x*inv_cell_size), int(y*inv_cell_size))
                        
                # Generates a point randomly selected around
                # the given point, between r and 2*r units away.
                def generate_random_around((x, y), r):
                        rr = uniform(r, 3*r)
                        rt = uniform(0, 2*pi)
                        return rr*sin(rt) + x, rr*cos(rt) + y
                        
                # Is the given point in the rectangle to be sampled?
                def in_rectangle((x, y)):
                        return 0 <= x < width and 0 <= y < height
                
                def do_it():
                
                        def in_neighbourhood(p, r):
                                gp = grid_coordinates(p)
                                r_sqr = r*r
                                
                                for cell in grid.square_iter(gp, 2):
                                        for q in cell:
                                                if sqr_dist(q, p) <= r_sqr:
                                                        return True
                                return False
                
                        #Create the grid
                        treelist = copy.deepcopy(self.AT) # create a copy of all trees so original is not modified
                        grid = ListGrid2D(( int(ceil(width/cell_size)),int(ceil(height/cell_size)) ))
                        in_rq = RandomQueue(treelist)
                        
                        out_rq = RandomQueue([])
                        #generate the first point
                        tree1 = in_rq.pop()
                        p = (rand(width), rand(height))
                        tree1.append(p)
                        grid[grid_coordinates(p)].append(p)
                        out_rq.push(tree1)

                        #generate other points from points in queue.
                        while not in_rq.empty():
                                tree1 = in_rq.pop()
                                p = (rand(width), rand(height))
                                tree1.append(p)
                                grid[grid_coordinates(p)].append(p)
                                out_rq.push(tree1)
                        return out_rq
                
                out_rq = do_it()
                print ' successfully placed points with overlap = %s...' % self.overlap
                # append points from AllTrees to the empty list at the end of plotTrees
                for i in out_rq.queue:
                        self.plotTrees[i[0]][-1].append(i[1])
                
                return self.plotTrees


