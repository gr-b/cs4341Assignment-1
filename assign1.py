# Randomly generate an n by m board.
# has spots 0-9, S, G, and #
import random, sys, time
spots = ['1','2','3','4','5','6','7','8','9','#','#','#']

def h1(node, board):
    return 0

def getGoalPosition(board):
    for row_i, row in enumerate(board):
        for col_i, col in enumerate(board):
            if board[row_i][col_i] == 'G':
                return row_i, col_i
    return None

def getVerticalAndHorizontalDistance(node, board):
    goal_position = getGoalPosition(board)
    vertical_distance = abs(goal_position[1] - node.col)  # get vertical distance
    horizontal_distance = abs(goal_position[0] - node.row)  # get horizontal distance

    return vertical_distance, horizontal_distance

def h2(node, board):
    vertical_distance, horizontal_distance = getVerticalAndHorizontalDistance(node, board)
    dist_to_use = min(vertical_distance, horizontal_distance)

    return dist_to_use

def h3(node, board):
    vertical_distance, horizontal_distance = getVerticalAndHorizontalDistance(node, board)

    dist_to_use = max(vertical_distance, horizontal_distance)

    return dist_to_use

# Manhattan distance
def h4(node, board):
    vertical_distance, horizontal_distance = getVerticalAndHorizontalDistance(node, board)


    return vertical_distance + horizontal_distance

def h5(node, board):
    """
    Add 1/3 of the current tile cost to Manhattan distance if the node is not facing
    the vertical direction of the goal
    Add 1/3 of the current tile cost to Manhattan Distance if the node is not facing
    the horizontal direction of the goal
    :param node:
    :return:
    """
    node_direction = node.direction
    node_col = node.col
    node_row = node.row
    node_cost = node.cost

    manhattan_distance = h4(node, board)

    goal_position = getGoalPosition(board)

    row_dist = goal_position[0] - node_row
    col_dist = goal_position[1] - node_col

    if (row_dist * node.direction[0] < 0) or (col_dist * node.direction[1] < 0):
        manhattan_distance += (1/3)
    if (row_dist * node.direction[0] < 0) and (col_dist * node.direction[1] < 0):
        manhattan_distance += (1/3)

    return manhattan_distance

def h6(node, board):
    return h5(node, board) * 3

def gen_board(n, m):
    board = [[random.choice(spots) for i in range(n)] for i in range(m)]
    board[random.randint(0,m-1)][random.randint(0,n-1)] = 'S'
    board[random.randint(0,m-1)][random.randint(0,n-1)] = 'G'
    return board


def print_board(board):
    bstr= ""
    for row in board:
        rowStr = ""
        for spot in row:
            if 'S' in spot or 'G' in spot:
                rowStr += "|" + spot + "|\t"
            else:
                rowStr+= spot + "\t"
        print(rowStr)

# Save board to file
def save_board(board, filename):
    f = open(filename,'w')
    for row in board:
        rowStr = ""
        for spot in row:
            rowStr+= spot + "\t"
        f.write(rowStr + '\n')
    f.close()

def read_board(filename):
    f = open(filename, 'r')
    boardStr = f.read(20000)
    chars = boardStr.split('\t')
    #print(chars)

    board = []
    row = []
    for c in chars:
        if "\n" in c:
            board += [row]
            row = []
            if len(c)>1:
                row += c[1]
        else:
            row += c

    f.close()
    return board

def getBranchingFactor(nodes, depth, tolerance):
    low = 0.0
    high = pow(nodes, 2.0/depth)
    while(True):
        avg = (low + high) / 2
        testNodes = 0
        for i in range(depth):
            testNodes += pow(avg, i+1)
        if(abs(testNodes - nodes) <= tolerance):
            return avg
        if(testNodes > nodes):
            high = avg
        else:
            low = avg

def addToList(node, queue):
    i = 0
    cost = node.cost + node.hCost
    while(i < len(queue) and cost < queue[i].cost + queue[i].hCost):
        i += 1
    queue.insert(i, node)
    
def getCost(str):
    if(str[0] == 'S' or str[0] == 'G'):
        return 1
    else:
        return int(str)

def inBoard(spot, board):
    return ((spot[0] < len(board[0])) and (spot[0] >= 0) and (spot[1] < len(board)) and (spot[1] >= 0))
    
def tryMove(node, queue, board, h, direction, turns, jump, appendList):
    newActions = list(node.actions)
    if(jump):
        dist = 3
    else:
        dist = 1
    spot = [node.col + dist*direction[0], node.row + dist*direction[1]]; #col, row (x, y)
    if(inBoard(spot, board)):
        boardVal = board[spot[1]][spot[0]]
        if(boardVal != "#"):
            for string in appendList:
                newActions.append(string)
            cost = node.cost + (1/3) * turns * getCost(board[node.row][node.col])
            if(jump):
                cost += 20
            else:
                cost += getCost(boardVal)
            n = Node(spot[1], spot[0], direction, cost, 0, list(newActions))
            n.d = node.d+1
            n.hCost = h(n, board)
            for qnode in queue:
                if qnode.row == n.row and qnode.col == n.col:
                    if n.cost > qnode.cost:
                        return 0
            for cnode in closed:
                if cnode.row == n.row and cnode.col == n.col:
                    if n.cost > cnode.cost:
                        return 0
            addToList(n, queue)
            return 1
    return 0

def expandNode(node, queue, board, h): 
    f = node.direction                     #        [0, -1]
    r = [-1*f[1], f[0]]                    #  [-1,0]       [1,0]
    l = [f[1], -1*f[0]]                    #        [0, 1]
    b = [-1*f[0], -1*f[1]]
    
    expanded = 0
    
    expanded += tryMove(node, queue, board, h, f, 0, 0, ["f"]) #forward
    expanded += tryMove(node, queue, board, h, f, 0, 1, ["j"]) #jump forward
    
    expanded += tryMove(node, queue, board, h, r, 1, 0, ["r", "f"]) #right
    expanded += tryMove(node, queue, board, h, r, 1, 1, ["r", "j"]) #jump right
    
    expanded += tryMove(node, queue, board, h, l, 1, 0, ["l", "f"]) #left
    expanded += tryMove(node, queue, board, h, l, 1, 1, ["l", "j"]) #jump left

    expanded += tryMove(node, queue, board, h, b, 2, 0, ["r", "r", "f"]) #back
    expanded += tryMove(node, queue, board, h, b, 2, 1, ["r", "r", "j"]) #jump back

    closed.append(node)

    return expanded


# queue - A sorted list of nodes to expand. Sorted based on the cost to
#   get to the node plus the heuristic cost. (starts continaing only the start node)
# h - The heuristic function to use. 
def search_node(start, board, h):
    expanded = 0
    generated = 0
    queue = [start]
    node = queue.pop()
    while(board[node.row][node.col][0] != 'G'):
        generated += expandNode(node, queue, board, h)
        node = queue.pop()
        expanded += 1
        #if expanded % 100 == 0:
        #    sys.stdout.write("|")
        #if expanded % 1000 == 0:
            #print(node.actions)
    #print("DEPTH: "  + str(node.d))
    #print(node.actions)
    #print("Score: " + str(500-node.cost))
    #print("Nodes expanded: " + str(expanded))
    return (node.actions, 500-node.cost, expanded, getBranchingFactor(generated, node.d, .001))

# Creates a node with the position of the s in the given board.
def get_initial_node(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 'S':
                row, col = (i, j)
    return Node(row, col, [0,-1], 0, 0, []) #row, col


class Node(object):
    def __init__(self, row, col, direction, cost, hCost, actions):
        self.col = col
        self.row = row
        self.direction = direction
        self.cost = cost
        self.hCost = hCost
        self.actions = actions
        self.d = 0;

def run_trial(board):
    print_board(board)
    heuristics = [h1, h2, h3, h4, h5, h6]
    heuristics.reverse()
    for h in heuristics:
        closed[:] = []
        initNode = get_initial_node(board)
        initNode.hCost = h(initNode, board)
        actions, score, expandedNodes, ebf = search_node(initNode, board, h)
        hString = str(h).split()[1]
        print("")
        #print(hString + " : Num Actions:" + str(len(actions)) + " | Score: " + str(score) + " | Expanded: " + str(expandedNodes) +  " | depth: " + str(depth)) #"| " + str(elapsed))
        print("Score:  " + str(score))
        print("Number of actions:  " + str(len(actions)))
        print("Number of nodes expanded:  " + str(expandedNodes))
        print("Estimated branching factor:  %.2f" % ebf);
        for action in actions:
            if action == "r":
                print("Turn Right")
            elif action == "l":
                print("Turn Left")
            elif action == "f":
                print("Forward")
            elif action == "j":
                print("Leap")
        print("")


def run_trial_single(board, h_number, heuristics):

    h = heuristics[h_number-1]
    initNode = get_initial_node(board)
    initNode.hCost = h(initNode, board)
    actions, score, expanded, ebf = search_node(initNode, board, h)
    hString = str(h).split()[1]
    print("")

    #print(hString + " : Num Actions: " + str(len(actions)) + " | Score: " + str(score) + " | Expanded: " + str(
    #    expanded) + " | depth: " + str(depth))  # "| " + str(elapsed))
    print("Score:  " + str(score))
    print("Number of actions:  " + str(len(actions)))
    print("Number of nodes expanded:  " + str(expanded))
    print("Estimated branching factor:  %.2f" % ebf);
    for action in actions:
        if action == "r":
            print("Turn Right")
        elif action == "l":
            print("Turn Left")
        elif action == "f":
            print("Forward")
        elif action == "j":
            print("Leap")
    print("")

closed = []

def main():
    """
    The command line takes in the filename and the heuristic number
    :return:
    """
    import os.path

    arguments = sys.argv

    if len(arguments) != 3:
        print("The input has to include two parameters: the file name of the board and the heuristic number to use.")
        exit()

    heuristics = [h1, h2, h3, h4, h5, h6]

    file_name = arguments[1]
    heuristic_number = int(arguments[2])


    if not 0 < heuristic_number <= len(heuristics):
        print("The heuristic has to be from range 0 to %s" % len(heuristics))
        exit()


    heuristics = [h1, h2, h3, h4, h5, h6]

    if not os.path.exists(file_name):
        print("The file %s was not found." % file_name)
        exit()

    board = read_board(file_name)

    run_trial_single(board, heuristic_number, heuristics)

if __name__ == '__main__':
    main()


#b = gen_board(10,10)#read_board("board1")
#s = get_initial_node(b)
