
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
