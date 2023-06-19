package main

type CellularAutomaton struct {
	bytes            []byte
	isTransformation bool
	state            []byte
}

func (automaton *CellularAutomaton) Evaluate() {
	result := make([]byte, len(automaton.bytes), len(automaton.bytes))
	for i := range automaton.bytes {
		leftIndex := i - 1
		if leftIndex < 0 {
			leftIndex += len(automaton.bytes)
		}
		rightIndex := (i + 1) % len(automaton.bytes)

		leftByte := int(automaton.bytes[leftIndex])
		currentByte := int(automaton.bytes[i])
		rightByte := int(automaton.bytes[rightIndex])

		currentByte = currentByte<<1 | (rightByte >> 7)
		currentByte = currentByte | ((leftByte & 1) << 9)
		if automaton.isTransformation {
			result[i] = automaton.evaluateTransformation(currentByte)
		} else {
			stateNumber := (uint16(automaton.state[i*2]) << 8) | uint16(automaton.state[i*2+1])
			result[i] = automaton.evaluateCompression(currentByte, stateNumber)
		}

	}
	automaton.bytes = result
}

func (automaton *CellularAutomaton) evaluateTransformation(number int) byte {
	return Rules30n105[number]
}

func (automaton *CellularAutomaton) evaluateCompression(number int, stateNumber uint16) byte {
	return StateRules[stateNumber][number]
}
