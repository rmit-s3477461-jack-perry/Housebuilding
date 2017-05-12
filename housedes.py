# -*- coding: cp1252 -*-

# AI4AD - GENETIC PROGRAMMING FOR ARCHITECTURAL SHAPES
#  ________                                     ________         ________
# |        |        |        |        |        |        |                |
# |        |        |        |        |        |        |                |
# |        |        |        |________|        |        |                |
# |        |        |                 |        |        |                |
# |        |________|                 |        |        |________________|
#
# INTERACTIVE AND MULTI-CRITERIA FITNESS EVALUATION

# Developed by Manuel Muehlbauer
# Under supervision of Jane Burry and Andy Song

# inspired by pygp package and gp.py


import random
import sys
import math
import System.Drawing as SD
import Rhino
import rhinoscriptsyntax as rs
from copy import deepcopy

pass  # *** RUN PARAMETERS ***


popcount = 50
genmax = 50

# Genetic Parameters

crossoverrate = 0.6
mutationrate = 0.2
eliterate = 0.2

# Crossover Parameters


pass  # *** INIT ***


pop = []
newpop = []

xval = []
yval = []

convx = []
convy = []

reportelite = []

global qmax
global houseTwo


def main(image, popcount = 50, crossoverrate = 0.7, mutationrate = 0.3, genmax = 50):
    global gen
    gen = 0
    trackelite = []
    
    matingpool_size = max(3, int(popcount / 10))
    tournament_size = max(3, int(popcount / 50))

    print("Loading preference image")
    preference = image
    prop = tuple([x/255 for x in preference])
    print(prop)

    print("Generating initial population")
    pop = new_population()


    for p in pop:

        while (gen < genmax) or (genmax == -1):  # Main Loop
            global allGeometry
            allGeometry = []
            # EVALUATION

            print("\nFinding Fitness:")
            for p in pop:
                p.Fitness = get_fitness(p, gen, prop)

            print("\nGetting Best of Generation:")
            pop.sort(key=lambda individuals: individuals.Fitness)
            for p in pop:
                print(p.Fitness)
            upperlimit = (int(popcount * eliterate))
            elite = pop[:upperlimit]

            # REPORTING BEST OF GENERATION
            print(elite, "this is the elitelist")
            qmax = elite[0]
            s = "\nIndividual " + str(qmax.Params) + ":" + str(qmax.Fitness)
            trackelite.append(qmax.Fitness)
            print(s)

            convx.append(gen)
            convy.append(qmax.Fitness)

            # SELECTION

            matecount = 0
            matingpool = []
            while matecount < matingpool_size:
                matingpool.append(tournament_select(pop, tournament_size))
                matecount += 1

            # CROSSOVER

            print("\nMating for generation " + str(gen) + ":")
            mated = mate_all(matingpool, popcount, crossoverrate)

            # MUTATION

            mutated = []
            print("\nMutating:")
            for i in range(0, int(popcount * mutationrate)):
                mutated.append(mutate(random.choice(pop)))
            pdot(1)

            # CREATE NEW GENERATION

            pop = elite + mated  + mutated
            elite = []
            mated = []
            mutated = []

            # ADVANCE GENERATION

            gen = gen + 1
    #generates geometry
    qmax.evaluate()
    listing = qmax.Params
    for i in range(0,6):
#        rs.EnableRedraw = False
        geo = add_geometry(elite[i])
        offset = 100
        x = i % 3 * offset
        y = i % 2 * offset
        rs.MoveObject(geo, x, y)

pass  # *** NODE CLASS DECLARATION ***

def progressBar():
    if 'gen' in globals():
        return gen

class Node:
    def __init__(self):
        self.Children = []
        self.Parameters = []
        self.OutType = None
        self.AcceptsTypes = None

    def evaluate(self):
        """receiving tree items in preorder sequence"""
        tempParams = []
        if self.Children:
            for i in range(0, len(self.Children)):
                tempParams.append(self.Parameters)
                self.Children[i].evaluate()
            self.Parameters = tempParams
        return tempParams

    def add(self):
        if self.Children:
            for i in range(0, len(self.Children)):
                if self.Children[i] is None:
                    self.Children[i] = self.select_node()
                    self.Children[i].add()
                else:
                    self.Children[i].add()

    def replace(self):
        if self.Children:
            for i in range(0, len(self.Children)):
                self.Children[i] = self.select_node()
                self.Children[i].replace()

    def select_node(self):
        for t in range(0, len(self.AcceptsTypes)):
            item = self.AcceptsTypes[t]
            if item == 'fInteger':
                n = NodeInteger()
                return n
            if item == 'fPoint':
                n = NodePoint()
                return n
            if item == 'fBoolean':
                n = NodeBoolean()
                return n
            else:
                return None

    def subtree(self):
        subTree = []
        if self.Children:
            for i in range(0, len(self.Children)):
                if self.Children[i] is not None:
                    subTree.append(self.Children[i])
        return subTree


pass  # *** NODE ROOT ***


class NodeRoot(Node):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fRoot']
        self.AcceptsTypes = ['fBuilding', 'fGarage']
        self.Children = [NodeBuilding(), NodeGarage(), NodeLeanTo(), NodeRoof(), NodeStories()]

    def evaluate(self):
        tempParams = []
        for c in self.Children:
            tempParams.append(c.evaluate())
        tempParams = [var for var in tempParams if var]
        self.Parameters = tempParams
        return self.Parameters


pass  # *** NODE PART ***


class NodePart(Node):
     def evaluate(self):
        tempParams = []
        for c in self.Children:
                tempParams.append(c.evaluate())
        self.Parameters = tempParams
        return self.Parameters


class NodeBuilding(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fBuilding']
        self.AcceptsTypes = ['fPoint']
        self.Children = [NodeOrigin(), NodeSecond(), NodeFeatureSelection()]


class NodeGarage(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fGarage']
        self.AcceptsTypes = ['fOrigin', 'fThird']
        self.Children = [NodeOrigin(), NodeThird()]


class NodeLeanTo(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fLeanTo']
        self.AcceptsTypes = ['fLeanToProportions']
        self.Children = [NodeBoolean(), NodeLeanToProportions()]


class NodeRoof(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fRoof']
        self.AcceptsTypes = ['fRoofProportions']
        self.Children = [NodeRoofProportions(), NodeRoofType()]


class NodeStories(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fFeature']
        self.AcceptsTypes = ['fInteger']
        self.Children = [None]


class NodeRoofType(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fFeature']
        self.AcceptsTypes = ['fInteger']
        self.Children = [None]


class NodeFeatureSelection(NodePart):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fFeatureSelection']
        self.AcceptsTypes = ['fVeranda', 'fBalcony', 'fChimney']
        self.Children = [NodeBalcony(), NodeChimney(), NodeStandingGable(), NodeTerrace(), NodeVeranda()]


pass  # *** NODE VALUES ***


class NodeValues(Node):
    def evaluate(self):
        return self.Parameters


class NodeOrigin(NodeValues):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fOrigin']
        self.Parameters = [0, 0, 0]


class NodeSecond(NodeValues):
    """Dimensions of the main building: more variation possible,
    height should reflect one or multiple stories."""
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fSecond']
        self.Parameters = [random.uniform(4, 10),
                           random.uniform(4, 10),
                           random.uniform(3.5, 3.9)]


class NodeThird(NodeValues):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fThird']
        self.Parameters = [(-1 * random.choice([3.2, 6.4, 9.6, 12.8])),
                           random.uniform(5.8, 6.2),
                           random.uniform(2.4, 3.2)]


class NodeRoofProportions(NodeValues):
    """Roof angle between 27 and 35 degrees"""
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fRoofProportions']
        self.Parameters = [random.uniform(2, 4),
                           random.uniform(0, 4),
                           random.uniform(1, 2),
                           random.uniform(0, 1)]


class NodeLeanToProportions(NodeValues):
    """Roof angle between 27 and 35 degrees"""
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fLeanToProportions']
        self.Parameters = [random.uniform(4, 7),
                           random.uniform(0, 1)]


pass  # *** NODE CLASS FEATURES ***


class NodeFeature(NodePart):
    """Abstract feature class, defining I/O switches."""
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fFeature']
        self.AcceptsTypes = ['fBoolean']
        self.Children = [None]


class NodeBalcony(NodeFeature):
    pass


class NodeChimney(NodeFeature):
    """One or two chimneys possible"""
    pass


class NodeStandingGable(NodeFeature):
    """Replaces on half of the initial veranda node."""
    pass


class NodeTerrace(NodeFeature):
    pass

class NodeVeranda(NodeFeature):
    pass


pass  # *** NODE CLASS BASICS ***


class NodeEmpty(NodeValues):
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fEmpty']
        self.AcceptsTypes = []
        self.Children = []


class NodeInteger(NodeValues):
    """used for the number of stories and rooftype"""
    def __init__(self):
        Node.__init__(self)
        self.OutType = ['fInteger']
        self.AcceptsTypes = None
        self.Parameters = random.randint(1, 3)


class NodeBoolean(NodeValues):
    def __init__(self):
        Node.__init__(self)
        self.OutType = 'fBoolean'
        self.AcceptsTypes = None
        self.Parameters = random.randint(0, 1)


pass  # *** SHAPE GRAMMAR ***


class Windows(NodeFeature):
    """Implement at the very end > shape grammar"""
    pass


pass  # ** INDIVIUAL ***


class Individual:
    def __init__(self):
        self.Events = [NodeRoot()]
        self.Params = []
        self.Fitness = None

    def initialize(self):
        self.Events[0].add()

    def evaluate(self):
        self.Params = self.Events[0].evaluate()
        return self.Params


pass  # *** FUNCTIONS ***

def load_image():
    filter = "BMP (*.bmp)|*.bmp|PNG (*.png)|*.png|JPG (*.jpg)|*.jpg|All (*.*)|*.*||"
    #filter = "PNG (*.png)|*.png"
    filename = rs.OpenFileName("Select image file", filter)

    if not filename: return

    # use the System.Drawing.Bitmap class described at
    # [url]http://msdn.microsoft.com/en-us/library/system.drawing.bitmap.aspx[/url]
    img = SD.Bitmap(filename)

    w = img.Width
    h = img.Height

    red = []
    green = []
    blue = []
    colourTuple = []
    sumR = 0
    sumG = 0
    sumB = 0
    N=0
    for x in range(w):
            for y in range(h):
                 color = img.GetPixel(x, y)
                 r = rs.ColorRedValue(color)
                 g = rs.ColorGreenValue(color)
                 b = rs.ColorBlueValue(color)
                 red.append(r)
                 green.append(g)
                 blue.append(b)
                 N += N
    for item in red:
        sumR += item
    colourTuple.append(sumR / len(red))
    for item in green:
        sumG += item
    colourTuple.append(sumG / len(green))
    for item in blue:
        sumB += item
    colourTuple.append(sumB / len(blue))

    print(colourTuple)
    return colourTuple, filename

def new_population():
    # Generates Initial Population
    global pop
    while len(pop) < popcount:
        I = Individual()
        I.initialize()
        pop = pop + [I]
    pdot(len(pop))
    return pop
    

def pdot(length):
    # Progress indicator
    for i in range(0, length):
        sys.stdout.write(".")

def get_fitness(ind, generation, proportion):
    """Get user value for fitness evaluation. This function is called for
       every infividual in the population."""
    ind.evaluate()
    listing = ind.Params
    stories = listing[4][0]
    resultStories = stories * listing[0][1][2]

    if gen%20 == 21:
        preview = []
        while True:
            rs.EnableRedraw(False)
            preview = add_geometry(listing)
            rs.EnableRedraw(True)
            # artificial selection
            fitnessValue = rs.GetInteger("Please enter the fitness value from 0 to 9 for the current shape", 0, 0, 9)
            if not fitnessValue:
                ind.Fitness = 0
                for p in preview: rs.DeleteObject(p)
                return
            else:
                ind.Fitness = fitnessValue
                for p in preview: rs.DeleteObject(p)
                return
    else:
        dX = listing[0][1][0]
        dY = listing[0][1][1]
        dZ = resultStories
        if dY > dX and dY > dZ:
            ind.Fitness = dY
        if dZ > dX and dZ > dY:
            ind.Fitness = dZ
#        normalize = (dX+dY+dZ)/3
#        ind.Fitness = dX/normalize - proportion[0] + dY/normalize - proportion[1] #+ dZ/normalize - proportion[2]
    return ind.Fitness

def tournament_select(fitness_lst, tournament_size):
    """Selects an individual according to tournament selection for maximisation
        problem. Returns the index in the fitness list corresponding to the
        selected individual."""
    tournament_best = None
    for n in range(0, tournament_size):
        ind = random.choice(fitness_lst)
        prog_fit = ind.Fitness
        if tournament_best is None:
            tournament_best = ind
        else:
            tour_fit = tournament_best.Fitness
            if prog_fit > tour_fit:
                tournament_best = ind
    return tournament_best

def mutate(Ind):
    newInd = deepcopy(Ind)
    newInd.Events[0].evaluate()
    random.choice(newInd.Events[0].Children[0].Children[2].subtree()).replace()
    newInd.Fitness = None
    return newInd

def mate_all(pool, popcount, crossoverrate):
    # perform mating on the entire population
    # kill the parents and replace With Children
    npop = []
    while len(npop) < int(popcount * crossoverrate):
        # produce new population by sexual crossover.
        npop = npop + mate(random.choice(pool),
                           random.choice(pool))
    pdot(len(npop))
    return npop

def mate(parentA, parentB):
    # sexually mate any number of nodes to make new nodes.

    childFirst = deepcopy(parentA)
    childSecond = deepcopy(parentB)

    nodechoice = random.randint(0, 1)
    childFirst.Events[0].Children[nodechoice] = parentB.Events[0].Children[nodechoice]
    childSecond.Events[0].Children[nodechoice] = parentA.Events[0].Children[nodechoice]

    childFirst.Fitness = 0
    childSecond.Fitness = 0

    return [childFirst, childSecond]


pass  # *** GEOMETRY ***


def add_geometry(listing):
    """generates the geometry for display in rhino"""
    rs.EnableRedraw(False)

    # *** HOUSE ***

    # STORIES

    stories = listing[4][0]
    resultStories = stories * listing[0][1][2]

    # SHAPE

    x1 = listing[0][0][0]
    y1 = listing[0][0][1]
    z1 = listing[0][0][2]
    x2 = listing[0][1][0]
    y2 = listing[0][1][1]
    z2 = resultStories
    A = [x1, y1, z1]
    B = [x1, y2, z1]
    C = [x2, y2, z1]
    D = [x2, y1, z1]

    E = [x1, y1, z2]
    F = [x1, y2, z2]
    G = [x2, y2, z2]
    H = [x2, y1, z2]
    allGeometry.append(rs.AddBox([A, B, C, D, E, F, G, H]))

    # *** FEATURES ***

    # BALCONY

    """add a balcony if boolean is true and stories greater 1"""
    if listing[0][2][3][0] == 1 and listing[4][0] > 1:
        side = 1
        heightStories = random.randint(1, listing[4][0]-1)
        heightBalcony = heightStories * listing[0][1][2]
        """select side for positioning of balcony
           side 0 is backside, then clockwise"""
        if side == 0:
            bx1 = random.uniform(1, x2-3)
            by1 = y2
            bz1 = heightBalcony
            bx2 = bx1 + 2
            by2 = y2 + 2
            bz2 = heightBalcony + 1.2
        if side == 1:
            bx1 = x2
            by1 = random.uniform(1, y2-3)
            bz1 = heightBalcony
            bx2 = x2 + 2
            by2 = by1 + 2
            bz2 = heightBalcony + 1.2
        if side == 2:
            bx1 = random.uniform(1, x2-3)
            by1 = y1
            bz1 = heightBalcony
            bx2 = bx1 + 2
            by2 = y1 - 2
            bz2 = heightBalcony + 1.2
        add_box(bx1, by1, bz1, bx2, by2, bz2)

    # CHIMNEY
    if listing[0][2][1][0] == 1:
        cx1 = random.uniform(2, x2-2.5)
        cy1 = random.uniform(2, y2-2.5)
        cz1 = z1
        cx2 = cx1 + 0.5
        cy2 = cy1 + 0.5
        if cx1 < x2 / 2:
            cz2 = z2 + 2 + math.sin(0.523) * cx1
        else:
            cz2 = z2 + 2 + math.sin(0.523) * -(cx1 - x2)
        add_box(cx1, cy1, cz1, cx2, cy2, cz2)

    # STANDING GABLE
    if listing[0][2][2][0] == 1:
        pass

    # TERRACE
    if listing[0][2][3][0] == 1:
        side = 1
        if side == 0:
            tx1 = random.uniform(1, x2-5)
            ty1 = y2
            tz1 = 0
            tx2 = tx1 + 4
            ty2 = y2 + 4
            tz2 = 0.2
        if side == 1:
            tx1 = x2
            ty1 = random.uniform(1, y2-5)
            tz1 = 0
            tx2 = x2 + 4
            ty2 = ty1 + 4
            tz2 = 0.2
        if side == 2:
            tx1 = random.uniform(1, x2-5)
            ty1 = y1
            tz1 = 0
            tx2 = tx1 + 2
            ty2 = y1 - 2
            tz2 = 0.2

        add_box(tx1, ty1, tz1, tx2, ty2, tz2)

    # VERANDA
    if listing[0][2][4][0] == 1:
        verandaZ = 1
        verandaOffsetRoof = 2
        thickness = 0.2
        verandaY1 = y1 - 3
        add_box(x1, y1, z1, x2, (y1 - 3), 0.2)
        bA = [x1, verandaY1, z2-verandaZ]
        bB = [x2, verandaY1, z2-verandaZ]
        cA = [x1, y1, z2-verandaZ]
        cB = [x2, y1, z2-verandaZ]
        tA = [x1 + verandaOffsetRoof, y1, z2]
        tB = [x2 - verandaOffsetRoof, y1, z2]
        pitch_roof(bA, bB, tA, tB, cA, cB)
        allGeometry.append(rs.AddSrfPt([bA, bB, cB, cA]))

        add_box(x1, verandaY1, z1, x1 + thickness, verandaY1 + thickness, z2-verandaZ)
        add_box(x1 + x2 / 3, verandaY1, z1, x1 + x2 / 3 + thickness, verandaY1 + thickness, z2-verandaZ)
        add_box(x1 + x2 * 2 / 3, verandaY1, z1, x1 + x2 * 2 / 3 + thickness, verandaY1 + thickness, z2-verandaZ)
        add_box(x2, verandaY1, z1, x2 - thickness, verandaY1 + thickness, z2-verandaZ)

    # *** GARAGE ***
    x3 = listing[1][0][0]
    y3 = listing[1][0][1]
    z3 = listing[1][0][2]
    x4 = listing[1][1][0]
    y4 = listing[1][1][1]
    z4 = listing[1][1][2]

    I = [x3, y3, z3]
    J = [x3, y4, z3]
    K = [x4, y4, z3]
    L = [x4, y3, z3]

    M = [x3, y3, z4]
    N = [x3, y4, z4]
    O = [x4, y4, z4]
    P = [x4, y3, z4]

    allGeometry.append(rs.AddBox([I, J, K, L, M, N, O, P]))

    # *** LEAN TO ***

    if listing[2][0] == 1:
        lY = listing[2][1][0]
        lZ = listing[2][1][1]
        add_box(x1, y2, z1, x2, (y2+lY), z2-lZ)
        bA = [x1, (y2+lY), z2-lZ]
        bB = [x2, (y2+lY), z2-lZ]
        cA = [x1, y2, z2-lZ]
        cB = [x2, y2, z2-lZ]
        pitch_roof(bA, bB, F, G, cA, cB)

    # *** ROOF ***

    yRoofGarage = listing[3][0][3]
    zRoofGarage = listing[3][0][2]

    yRoofHouse = listing[3][0][1]
    zRoofHouse = listing[3][0][0]
    if listing[3][1][0] == 0: #both double pitch
        double_pitch(E, F, G, H, yRoofHouse, zRoofHouse)
        double_pitch(M, N, O, P, yRoofGarage, zRoofGarage)
    if listing[3][1][0] == 1: #both dutch gable
        dutch_gable(E, F, G, H, yRoofHouse, zRoofHouse)
        dutch_gable(M, N, O, P, yRoofGarage, zRoofGarage)
    if listing[3][1][0] == 2: #one each one way
        double_pitch(E, F, G, H, yRoofHouse, zRoofHouse)
        dutch_gable(M, N, O, P, yRoofGarage, zRoofGarage)
    if listing[3][1][0] == 3: #one each other way
        dutch_gable(E, F, G, H, yRoofHouse, zRoofHouse)
        double_pitch(M, N, O, P, yRoofGarage, zRoofGarage)

    # REMOVE UNNECESSARY GEOMETRY

    rs.DeleteObjects(rs.ObjectsByType(1, True))
    rs.DeleteObjects(rs.ObjectsByType(4, True))

    rs.EnableRedraw(True)

    return allGeometry

def add_box(vx1, vy1, vz1, vx2, vy2, vz2):
        vA = [vx1, vy1, vz1]
        vB = [vx1, vy2, vz1]
        vC = [vx2, vy2, vz1]
        vD = [vx2, vy1, vz1]
        vE = [vx1, vy1, vz2]
        vF = [vx1, vy2, vz2]
        vG = [vx2, vy2, vz2]
        vH = [vx2, vy1, vz2]
        allGeometry.append(rs.AddBox([vA, vB, vC, vD, vE, vF, vG, vH]))

def double_pitch(m, n, o, p, diffY, diffZ):
    """generates a double pitch roof"""
    # cullis
    cullisN = rs.AddLine(m, n)
    cullisP = rs.AddLine(p, o)

    # ridge
    cullisO = rs.AddLine(n, o)
    domainO = rs.CurveDomain(cullisO)

    cullisM = rs.AddLine(p, m)
    domainM = rs.CurveDomain(cullisM)

    midCullisO = rs.EvaluateCurve(cullisO, (domainO[1] / 2.0))
    midCullisM = rs.EvaluateCurve(cullisM, (domainM[1] / 2.0))
    
    ridgeM = rs.PointAdd(rs.PointAdd(midCullisM, [0, 0, diffZ]), [0, diffY, 0])
    ridgeO = rs.PointAdd(rs.PointAdd(midCullisO, [0, 0, diffZ]), [0, -diffY, 0])
    ridge = rs.AddLine(ridgeM, ridgeO)

    allGeometry.append(rs.AddLoftSrf([cullisN, ridge]))
    allGeometry.append(rs.AddLoftSrf([cullisP, ridge]))

    # gable
    ridgeOPt = ridgeO
    ridgeMPt = ridgeM
#    print(m)
#    print(ridgeMPt)
#    print(p)
    allGeometry.append(rs.AddSrfPt([m, ridgeMPt, p]))
    allGeometry.append(rs.AddSrfPt([n, ridgeOPt, o]))

def dutch_gable(e, f, g, h, diffY, diffZ):
    """generates a dutch gable roof"""
    cullisG = rs.AddLine(f, g)
    domainG = rs.CurveDomain(cullisG)

    cullisE = rs.AddLine(h, e)
    domainE = rs.CurveDomain(cullisE)

    midCullisG = rs.EvaluateCurve(cullisG, (domainG[1]/2.0))
    midCullisE = rs.EvaluateCurve(cullisE, (domainE[1]/2.0))

    ridgeE = rs.PointAdd(rs.PointAdd(midCullisE, [0, 0, diffZ]), [0, diffY, 0])
    ridgeG = rs.PointAdd(rs.PointAdd(midCullisG, [0, 0, diffZ]), [0, -diffY, 0])
    ridge = rs.AddLine(ridgeE, ridgeG)

    diagonalEdgeF = rs.AddLine(f, ridgeG)
    diagonalEdgeG = rs.AddLine(g, ridgeG)
    diagonalEdgeH = rs.AddLine(h, ridgeE)
    diagonalEdgeE = rs.AddLine(e, ridgeE)

    domainDEdgeF = rs.CurveDomain(diagonalEdgeF)
    domainDEdgeG = rs.CurveDomain(diagonalEdgeG)
    domainDEdgeH = rs.CurveDomain(diagonalEdgeH)
    domainDEdgeE = rs.CurveDomain(diagonalEdgeE)

    dutchGablePointF = rs.EvaluateCurve(diagonalEdgeF, (domainDEdgeF[1]*5/7.0))
    dutchGablePointG = rs.EvaluateCurve(diagonalEdgeG, (domainDEdgeG[1]*5/7.0))
    dutchGablePointH = rs.EvaluateCurve(diagonalEdgeH, (domainDEdgeH[1]*5/7.0))
    dutchGablePointE = rs.EvaluateCurve(diagonalEdgeE, (domainDEdgeE[1]*5/7.0))

    allGeometry.append(rs.AddSrfPt([f, dutchGablePointF, dutchGablePointG, g]))
    allGeometry.append(rs.AddSrfPt([h, dutchGablePointH, dutchGablePointE, e]))
    allGeometry.append(rs.AddSrfPt([f, dutchGablePointF, dutchGablePointE, e]))
    allGeometry.append(rs.AddSrfPt([h, dutchGablePointH, dutchGablePointG, g]))

   # cullis
    cullisDutchGableF = rs.AddLine(dutchGablePointE, dutchGablePointF)
    cullisDutchGableH = rs.AddLine(dutchGablePointH, dutchGablePointG)

    # ridge
    cullisDutchGableG = rs.AddLine(dutchGablePointF, dutchGablePointG)
    domainDutchGableG = rs.CurveDomain(cullisDutchGableG)

    cullisDutchGableE = rs.AddLine(dutchGablePointH, dutchGablePointE)
    domainDutchGableE = rs.CurveDomain(cullisDutchGableE)

    midDGCullisG = rs.EvaluateCurve(cullisDutchGableG, (domainDutchGableG[1]/2.0))
    midDGCullisE = rs.EvaluateCurve(cullisDutchGableE, (domainDutchGableE[1]/2.0))

    XmidDGCullisG = midDGCullisG[0]
    XmidDGCullisE = midDGCullisE[0]
    YmidDGCullisG = midDGCullisG[1]
    YmidDGCullisE = midDGCullisE[1]

    ZmidCullisG = midCullisG[2]
    ZmidCullisE = midCullisE[2]

    ridgeDutchGableE = [XmidDGCullisE, YmidDGCullisE, diffZ + ZmidCullisE]
    ridgeDutchGableG = [XmidDGCullisG, YmidDGCullisG, diffZ + ZmidCullisG]
    ridgeDutchGable = rs.AddLine(ridgeDutchGableE, ridgeDutchGableG)

    allGeometry.append(rs.AddLoftSrf([cullisDutchGableF, ridgeDutchGable]))
    allGeometry.append(rs.AddLoftSrf([cullisDutchGableH, ridgeDutchGable]))

    # gable
    ridgeDutchGableGPt = ridgeDutchGableG
    ridgeDutchGableEPt = ridgeDutchGableE
    allGeometry.append(rs.AddSrfPt([dutchGablePointE, ridgeDutchGableEPt, dutchGablePointH]))
    allGeometry.append(rs.AddSrfPt([dutchGablePointF, ridgeDutchGableGPt, dutchGablePointG]))

def pitch_roof(bA, bB, tA, tB, cA, cB):
    cullisBottom = rs.AddLine(bA, bB)
    cullisTop = rs.AddLine(tA, tB)

    allGeometry.append(rs.AddLoftSrf([cullisBottom, cullisTop]))
    allGeometry.append(rs.AddSrfPt([bA, tA, cA]))
    allGeometry.append(rs.AddSrfPt([bB, tB, cB]))

pass  # *** MAIN IMPLEMENTATION ***




pass  # *** OUTPUT ***

#print(qmax.Events[0].Children)

#for g in range(0, gen-1):
#    rs.AddPoint(convx[g] *20, convy[g] *20, 0)
