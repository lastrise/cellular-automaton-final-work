package main

import "sync"

type ParallelCellularAutomatonParams struct {
	data                   []byte
	countGoroutines        int
	countEvaluations       int
	callbackAfterEvolution func([]byte, int, int)
}

type CharChannel struct {
	left  chan byte
	right chan byte
}

type ParallelCellularAutomaton struct {
	CellularAutomaton
	countEvaluations          int
	countGoroutines           int
	singleCellularAutomatons  []*CellularAutomaton
	cellularAutomatonChannels []*CharChannel
	singleAutomatonsGroup     sync.WaitGroup
	callbackAfterEvolution    func([]byte, int, int)
}

func (automaton *ParallelCellularAutomaton) distributeBytes() [][]byte {
	distribution := make([][]byte, automaton.countGoroutines)
	perGoroutine := len(automaton.bytes) / automaton.countGoroutines
	for i := 0; i < automaton.countGoroutines; i++ {
		partition := append([]byte(nil), automaton.bytes[perGoroutine*i:perGoroutine*(i+1)]...)
		if i == automaton.countGoroutines-1 {
			partition = append(partition, automaton.bytes[perGoroutine*(i+1):]...)
		}
		if i == 0 {
			partition = append(automaton.bytes[len(automaton.bytes)-1:], partition...)
			partition = append(partition, automaton.bytes[perGoroutine])
		} else if i == automaton.countGoroutines-1 {
			partition = append(partition, automaton.bytes[0])
			partition = append(automaton.bytes[perGoroutine*(i-1)+perGoroutine-1:perGoroutine*(i-1)+perGoroutine], partition...)
		} else {
			partition = append(automaton.bytes[perGoroutine*(i-1)+perGoroutine-1:perGoroutine*(i-1)+perGoroutine], partition...)
			partition = append(partition, automaton.bytes[perGoroutine*(i+1)])
		}
		distribution[i] = partition
	}
	return distribution
}

func (automaton *ParallelCellularAutomaton) evaluate(singleAutomaton *CellularAutomaton, indexAutomaton int) {
	for i := 0; i < automaton.countEvaluations; i++ {
		singleAutomaton.Evaluate()

		intermediate := singleAutomaton.bytes[1 : len(singleAutomaton.bytes)-1]
		leftChar := intermediate[0]
		rightChar := intermediate[len(intermediate)-1]

		if automaton.callbackAfterEvolution != nil {
			perGoroutine := len(automaton.bytes) / automaton.countGoroutines
			automaton.callbackAfterEvolution(intermediate, i, perGoroutine*indexAutomaton)
		}

		leftChannelIndex := indexAutomaton - 1
		rightChannelIndex := indexAutomaton + 1
		if indexAutomaton == 0 {
			leftChannelIndex = automaton.countGoroutines - 1
		}
		if indexAutomaton == automaton.countGoroutines-1 {
			rightChannelIndex = 0
		}

		automaton.cellularAutomatonChannels[leftChannelIndex].right <- leftChar
		automaton.cellularAutomatonChannels[rightChannelIndex].left <- rightChar

		singleAutomaton.bytes[0] = <-automaton.cellularAutomatonChannels[indexAutomaton].left
		singleAutomaton.bytes[len(singleAutomaton.bytes)-1] = <-automaton.cellularAutomatonChannels[indexAutomaton].right
	}

	automaton.singleAutomatonsGroup.Done()
}

func (automaton *ParallelCellularAutomaton) createSingleAutomatons() {
	distribution := automaton.distributeBytes()
	automaton.singleCellularAutomatons = make([]*CellularAutomaton, 0, 0)
	for _, packet := range distribution {
		automaton.singleCellularAutomatons = append(automaton.singleCellularAutomatons,
			&CellularAutomaton{bytes: packet, isTransformation: true})
		automaton.cellularAutomatonChannels = append(automaton.cellularAutomatonChannels,
			&CharChannel{left: make(chan byte, 2), right: make(chan byte, 2)})
	}
}

func (automaton *ParallelCellularAutomaton) Evaluate() {
	for i, singleAutomaton := range automaton.singleCellularAutomatons {
		automaton.singleAutomatonsGroup.Add(1)
		go automaton.evaluate(singleAutomaton, i)
	}
	automaton.singleAutomatonsGroup.Wait()

	result := make([]byte, 0, len(automaton.bytes))
	for _, singleAutomaton := range automaton.singleCellularAutomatons {
		result = append(result, singleAutomaton.bytes[1:len(singleAutomaton.bytes)-1]...)
	}
	automaton.bytes = result
}

func CreateParallelCellularAutomaton(params *ParallelCellularAutomatonParams) *ParallelCellularAutomaton {
	automaton := ParallelCellularAutomaton{}
	automaton.bytes = params.data

	automaton.countGoroutines = params.countGoroutines
	automaton.countEvaluations = params.countEvaluations
	automaton.callbackAfterEvolution = params.callbackAfterEvolution
	automaton.createSingleAutomatons()
	return &automaton
}
