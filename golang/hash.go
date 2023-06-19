package main

import "C"
import (
	"encoding/binary"
	"math"
	"unsafe"
)

type HashFunction struct {
	transform                 []byte
	blockSize                 int
	state                     []byte
	iterationsBeforeTransform int
	iterationsCompression     int
}

func (h *HashFunction) transformCallback(bytes []byte, iteration int, offset int) {
	if iteration < h.iterationsBeforeTransform {
		return
	}
	iteration -= h.iterationsBeforeTransform

	blockOffset := offset % h.blockSize
	iterationByte := h.blockSize - iteration/8 - 1
	blockStart := (offset/h.blockSize)*h.blockSize + iterationByte
	indexByte := iterationByte - blockOffset
	iterationOffset := iteration % 8

	if indexByte < 0 {
		indexByte += h.blockSize
		blockStart += h.blockSize
	}

	for indexByte < len(bytes) {
		h.transform[blockStart] |= ((bytes[indexByte] >> iterationOffset) & 1) << iterationOffset
		blockStart += h.blockSize
		indexByte += h.blockSize
	}
}

func makePadding(length int, blockSize int) []byte {
	tmp := make([]byte, blockSize+8, blockSize+8) // padding + length buffer
	tmp[0] = 0x80
	var t uint64
	if length%blockSize < blockSize-8 {
		t = uint64(blockSize - 8 - length%blockSize)
	} else {
		t = uint64(blockSize + blockSize - 8 - length%blockSize)
	}
	// Length in bits.
	length <<= 3
	padlen := tmp[:t+8]
	binary.BigEndian.PutUint64(padlen[t+0:], uint64(length))
	return padlen
}

func (h *HashFunction) Hash(message []byte) []byte {
	padding := makePadding(len(message), h.blockSize)
	h.transform = make([]byte, len(message)+len(padding))
	message = append(message, padding...)
	countGoroutines := int(math.Min(25, float64(len(message))))
	params := &ParallelCellularAutomatonParams{
		data: message, countGoroutines: countGoroutines, countEvaluations: h.blockSize*8 + h.iterationsBeforeTransform, callbackAfterEvolution: h.transformCallback}
	automaton := CreateParallelCellularAutomaton(params)
	automaton.Evaluate()
	h.state = make([]byte, h.blockSize*2)
	for i := 0; i < h.blockSize*2; i++ {
		h.state[i] = h.transform[i%h.blockSize]
	}

	for i := 0; i < len(message)/h.blockSize; i++ {
		single := CellularAutomaton{bytes: message[i*h.blockSize : i*h.blockSize+h.blockSize], state: h.state}
		for j := 0; j < h.iterationsCompression; j++ {
			single.Evaluate()
		}
		for j := 0; j < h.blockSize*2; j++ {
			h.state[j] = h.transform[i*h.blockSize+j%h.blockSize] ^ single.bytes[j%h.blockSize]
		}
		single.state = h.state
	}

	return h.state[:h.blockSize]
}

func Hash128(message []byte) []byte {
	hash := new(HashFunction)
	hash.blockSize = 16
	hash.iterationsBeforeTransform = 50
	hash.iterationsCompression = 15
	return hash.Hash(message)
}

func Hash256(message []byte) []byte {
	hash := new(HashFunction)
	hash.blockSize = 32
	hash.iterationsBeforeTransform = 50
	hash.iterationsCompression = 15
	return hash.Hash(message)
}

func HashExperimental(blockSize int, iterationsBeforeTransform int, iterationsCompression int, message []byte) []byte {
	hash := new(HashFunction)
	hash.blockSize = blockSize
	hash.iterationsBeforeTransform = iterationsBeforeTransform
	hash.iterationsCompression = iterationsCompression
	return hash.Hash(message)
}

//export ExperimentalAutomatonHash
func ExperimentalAutomatonHash(blockSize int, iterationsBeforeTransform int, iterationsCompression int, message []byte) unsafe.Pointer {
	return C.CBytes(HashExperimental(blockSize, iterationsBeforeTransform, iterationsCompression, message))
}
