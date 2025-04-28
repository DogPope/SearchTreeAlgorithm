class SearchTreeNode:
  def __init__(self, game_board, current_player, ply=0, max_depth=3):
    self.children = []
    self.value_is_assigned = False
    self.ply_depth = ply
    self.current_board = game_board
    self.move_for = current_player

    if self.ply_depth < max_depth and self.current_board.state_of_board() == "U": # Base Case
      self.generate_children(max_depth)
    else: # Evaluate the board position
      player_score, computer_score = self.current_board.count_score()
      self.value = computer_score - player_score  # Maximize Computer chance
      self.value_is_assigned = True

  def min_max_value(self, max_depth):
    if self.value_is_assigned:
      return self.value
    for child in self.children:
      child.min_max_value(max_depth)
    if self.move_for == 2: # Max Computer
      if not self.children:
        self.value = -999  # Negative Reinforcement Copmuter
      else:
        self.value = max(child.value for child in self.children)
    else: # Minimizing Player
      if not self.children:
        self.value = 999  # Very good for computer if human has no moves
      else:
        self.value = min(child.value for child in self.children)
    self.value_is_assigned = True
    return self.value

  def generate_children(self, max_depth):
    for next_board in self.current_board.all_possible_moves():
      self.children.append(SearchTreeNode(next_board, 3 - self.move_for, ply=self.ply_depth+1, max_depth=max_depth))


'''Map of the Game board for reference. It's long for easier deciphering of indices.'''
#      [0,1]     [0,3]     [0,5]
# [1,0]     [1,2]     [1,4]     [1,6]
#      [2,1]     [2,3]     [2,5]
# [3,0]     [3,2]     [3,4]     [3,6]
#      [4,1]     [4,3]     [4,5]
class DotsAndBoxes:
  def __init__(self, newBoard=None, current_player=1, player_score=0, computer_score=0):
    self.current_player = current_player
    self.player_score = player_score
    self.computer_score = computer_score
    
    if newBoard is None:
      self.game_board = [
        ["*", " ", "*", " ", "*", " ", "*"],
        [" ", "0", " ", "0", " ", "0", " "],
        ["*", " ", "*", " ", "*", " ", "*"],
        [" ", "0", " ", "0", " ", "0", " "],
        ["*", " ", "*", " ", "*", " ", "*"]
      ]
    else:
      self.game_board = [row[:] for row in newBoard]  # Deep copy of board
    
    self.state = self.state_of_board()

  def display_board(self):
    for row in self.game_board:
      print(''.join(row))

  def state_of_board(self):
    # Game is ongoing if there are still moves available
    if self.return_available_moves():
      return "U"  # Undecided
    else:
      return "D"  # Done

  def return_available_moves(self):
    remaining_moves = []
    for row_index in range(len(self.game_board)):
      for col_index in range(len(self.game_board[row_index])):
        if self.game_board[row_index][col_index] == " ":
          # Only add valid line positions (not box centers or dots)
          if (row_index % 2 == 0 and col_index % 2 == 1) or (row_index % 2 == 1 and col_index % 2 == 0):
            remaining_moves.append((row_index, col_index))
    return remaining_moves

  def all_possible_moves(self):
    remaining_moves = self.return_available_moves()
    all_moves = []
    
    for move in remaining_moves:
      # Create a new board with this move
      new_board = DotsAndBoxes([row[:] for row in self.game_board], 
                              self.current_player,
                              self.player_score,
                              self.computer_score)
      
      # Apply the move
      new_board.add_line(move[0], move[1])
      
      # Check if any boxes were completed
      boxes_completed = new_board.check_if_box_completed(move[0], move[1])
      
      # Change player if no boxes were completed
      if boxes_completed == 0:
        new_board.change_player()
        
      all_moves.append(new_board)
    
    return all_moves

  def check_if_box_completed(self, row, col):
    boxes_completed = 0

    if row % 2 == 0: # Handle horizontal line
      # Check box above (if exists)
      if row > 0:
        r, c = row - 1, col
        if self.game_board[r][c] == "0" and self.count_lines_around_box(r, c) == 4:
          self.game_board[r][c] = str(self.current_player)
          if self.current_player == 1:
            self.player_score += 1
          else:
            self.computer_score += 1
          boxes_completed += 1
      
      # Check box below (if exists)
      if row < len(self.game_board) - 1:
        r, c = row + 1, col
        if self.game_board[r][c] == "0" and self.count_lines_around_box(r, c) == 4:
          self.game_board[r][c] = str(self.current_player)
          if self.current_player == 1:
            self.player_score += 1
          else:
            self.computer_score += 1
          boxes_completed += 1
    
    # Handle vertical line
    else:
      # Check box to the left (if exists)
      if col > 0:
        r, c = row, col - 1
        if self.game_board[r][c] == "0" and self.count_lines_around_box(r, c) == 4:
          self.game_board[r][c] = str(self.current_player)
          if self.current_player == 1:
            self.player_score += 1
          else:
            self.computer_score += 1
          boxes_completed += 1
      if col < len(self.game_board[row]) - 1: # Check box to the right (if exists)
        r, c = row, col + 1
        if self.game_board[r][c] == "0" and self.count_lines_around_box(r, c) == 4:
          self.game_board[r][c] = str(self.current_player)
          if self.current_player == 1:
            self.player_score += 1
          else:
            self.computer_score += 1
          boxes_completed += 1
    return boxes_completed

  def count_lines_around_box(self, row, col): #Count how many lines are drawn around a box center at (row, col)
    if self.game_board[row][col] not in ["0", "1", "2"]:
      return 0
    count = 0
    if row > 0 and self.game_board[row-1][col] == "-": # Check top
      count += 1
    if row < len(self.game_board)-1 and self.game_board[row+1][col] == "-": # Check bottom
      count += 1
    if col > 0 and self.game_board[row][col-1] == "-": # Check left
      count += 1
    if col < len(self.game_board[row])-1 and self.game_board[row][col+1] == "-": # Check right
      count += 1
    return count

  def count_score(self):
    self.player_score = sum(row.count("1") for row in self.game_board)
    self.computer_score = sum(row.count("2") for row in self.game_board)
    return self.player_score, self.computer_score

  def change_player(self):
    self.current_player = 3 - self.current_player  # Switches between 1 and 2

  def player_move(self):
    remaining_moves = self.return_available_moves()
    player_score, computer_score = self.count_score()
    print(f"Player Score: {player_score}")
    print(f"Computer Score: {computer_score}")
    print(f"Available Moves: {remaining_moves}")
    
    try:
      row = int(input("Please enter a row for the move (0-4): "))
      col = int(input("Please enter a column for the move (0-6): "))
      if (row, col) not in remaining_moves:
        print("Invalid move. Please try again.")
        return False
    except ValueError:
      print("Please enter valid numbers.")
      return False
      
    self.add_line(row, col)
    boxes_completed = self.check_if_box_completed(row, col)
    if boxes_completed == 0:
      self.change_player()
    else:
      print(f"You completed {boxes_completed} box(es)! Take another turn.")
    return True

  def add_line(self, row, col):
    self.game_board[row][col] = "-"

  def computer_move(self):
    # First strategy: Look for boxes that can be completed
    move = self.find_completable_box()
    
    # Second strategy: Avoid giving away boxes
    if not move:
      move = self.find_safe_move()
    
    # If no strategic move found, use minimax for deeper analysis
    if not move:
      # Create a search tree with depth 2 (not too deep to be slow)
      search_tree = SearchTreeNode(self, self.current_player, max_depth=2)
      search_tree.min_max_value(2)
      
      # Find the best move for the computer
      best_value = float("-inf")
      best_board = None
      
      for child in search_tree.children:
        if child.value > best_value:
          best_value = child.value
          best_board = child.current_board
      
      # If we found a good move, determine what changed to make this move
      if best_board:
        for r in range(len(self.game_board)):
          for c in range(len(self.game_board[r])):
            if (self.game_board[r][c] == " " and 
                best_board.game_board[r][c] == "-"):
              move = (r, c)
                
    if not move: # If still no move (shouldn't happen), just take first available
      moves = self.return_available_moves()
      if moves:
        move = moves[0]
      else:
        print("No moves available for computer.")
        return
    
    print(f"Computer chose move: {move}")
    self.add_line(move[0], move[1])
    boxes_completed = self.check_if_box_completed(move[0], move[1])
    if boxes_completed > 0:
      print(f"Computer completed {boxes_completed} box(es) and gets another turn!")
      self.display_board()
      self.computer_move()  # Take another turn
    else:
      self.change_player()

  def find_completable_box(self): # Find a box that can be easily completed, i.e 3 adjacent lines.
    for r in range(len(self.game_board)):
      for c in range(len(self.game_board[r])):
        if self.game_board[r][c] == "0":  # Box center
          # If box has 3 lines, find the missing line
          if self.count_lines_around_box(r, c) == 3:
            # Check each side
            if r > 0 and self.game_board[r-1][c] == " ":  # Top
              return (r-1, c)
            if r < len(self.game_board)-1 and self.game_board[r+1][c] == " ":  # Bottom
              return (r+1, c)
            if c > 0 and self.game_board[r][c-1] == " ":  # Left
              return (r, c-1)
            if c < len(self.game_board[r])-1 and self.game_board[r][c+1] == " ":  # Right
              return (r, c+1)
    return None

  def find_safe_move(self): # Find a move that does not give away a box.
    safe_moves = []
    
    for move in self.return_available_moves():
      # Check if this move would create a box with 3 sides
      gives_away_box = False
      
      # Make a copy and test the move
      test_board = [row[:] for row in self.game_board]
      test_board[move[0]][move[1]] = "-"
      
      # Check nearby boxes
      box_positions = []
      
      # For horizontal line
      if move[0] % 2 == 0:
        if move[0] > 0:  # Box above
          box_positions.append((move[0] - 1, move[1]))
        if move[0] < len(test_board) - 1:  # Box below
          box_positions.append((move[0] + 1, move[1]))
      # For vertical line
      else:
        if move[1] > 0:  # Box to the left
          box_positions.append((move[0], move[1] - 1))
        if move[1] < len(test_board[move[0]]) - 1:  # Box to the right
          box_positions.append((move[0], move[1] + 1))
      
      for box_r, box_c in box_positions: # Check each box
        if (0 <= box_r < len(test_board) and 
            0 <= box_c < len(test_board[box_r]) and 
            test_board[box_r][box_c] == "0"):

          line_count = 0 # Count lines around this box
          if box_r > 0 and (test_board[box_r-1][box_c] == "-"):
            line_count += 1
          if box_r < len(test_board)-1 and (test_board[box_r+1][box_c] == "-"):
            line_count += 1
          if box_c > 0 and (test_board[box_r][box_c-1] == "-"):
            line_count += 1
          if box_c < len(test_board[box_r])-1 and (test_board[box_r][box_c+1] == "-"):
            line_count += 1
          
          if line_count == 3:
            gives_away_box = True
            break
      
      if not gives_away_box:
        safe_moves.append(move)
    if safe_moves:
      return safe_moves[0]
    
    return None

  def play_game(self):
    print("Welcome to Dots and Boxes!")
    print("Player: 1, Computer: 2")
    self.display_board()
    
    while self.state_of_board() == "U":
      if self.current_player == 1:
        print("\nYour turn!")
        valid_move = self.player_move()
        while not valid_move:
          valid_move = self.player_move()
      else:
        print("\nComputer's turn!")
        self.computer_move()
      
      self.display_board()
      player_score, computer_score = self.count_score()
      print(f"Current Score - Player: {player_score}, Computer: {computer_score}")
    
    # Game over
    print("\nGame Over!")
    player_score, computer_score = self.count_score()
    print(f"Final Score - Player: {player_score}, Computer: {computer_score}")
    
    if player_score > computer_score:
      print("Congratulations! You won!")
    elif player_score < computer_score:
      print("Computer wins!")
    else:
      print("It's a draw!")

# To play the game
if __name__ == "__main__":
  game = DotsAndBoxes()
  game.play_game()