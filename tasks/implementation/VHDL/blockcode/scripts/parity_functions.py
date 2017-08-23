#!/usr/bin/env python3
def create_parity_equations(chosen_parities):
    equations = []
    for parity in chosen_parities:
        data_positions=[]
        for position in range(0, len(parity)):
            if parity[position] == '1':
                data_positions.append('d[' + str(position) + ']')

        equation = '^'.join(data_positions)
        equations.append(equation)

    return equations

def create_parity_check(equations, d):
    parity_sum = ""
    for equation in equations:
        parity_sum += str(eval(equation))
    return parity_sum

