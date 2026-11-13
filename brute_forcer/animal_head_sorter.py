from collections import deque

def is_solved(state, capacity=4):
	"""
	Checks if every tube is either empty or full of a single animal type.
	"""
	for tube in state:
		if len(tube) == 0:
			continue
		if len(tube) != capacity or len(set(tube)) != 1:
			return False
	return True


def get_top_group_count(tube):
	"""
	Counts how many identical animals are stacked together at the top of a tube.
	"""
	if not tube:
		return 0
	top_animal = tube[-1]
	count = 0
	for animal in reversed(tube):
		if animal == top_animal:
			count += 1
		else:
			break
	return count


def solve_puzzle(initial_state, capacity=4):
	"""
	master function that will calculate and show the minimum number of moves
	needed to solve the sorting puzzle with minimum space
	"""

	# Queue stores tuples of: (current_board_state, number_of_moves_taken)
	queue = deque([(initial_state, [])])
	visited = {initial_state}
	pass


if __name__ == '__main__':
	# PUZZLE STEP
	# Represented from bottom (index 0) to top (last index)
	initial_tubes = (
		('chick', 'chick', 'chick', 'pig'),  # Tube 1
		('pig', 'elephant', 'elephant','pig'),  # Tube 2
		('chick', 'frog', 'elephant'),  # Tube 3
		('frog','frog', 'elephant'),  # Tube 4
		('frog', 'pig'),  # Tube 5
	)

	solution = solve_puzzle(initial_tubes)
	if solution:
		print(f"Solved in {len(solution)} moves!\n")
		for step_num, move in enumerate(solution, 1):
			print(f"{step_num}. {move}")
	else:
		print("No solution found.")
