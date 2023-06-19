package main

import "C"
import (
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
)

func help() {
	fmt.Println("Example usage:")
	fmt.Println(os.Args[0], "$1 $2 $3")
	fmt.Println("$1 BlockSize in bytes; should be value of [16, 32]")
	fmt.Println("$2 IterationsBeforeTransform [optional, will be used predefined value if not passed]")
	fmt.Println("$3 CompressionIterations [optional, will be used predefined value if not passed]")
	fmt.Println("$2 and $3 required both if passed one of them")
	fmt.Println("$2 and $3 should be > 0")
	os.Exit(1)
}

func parseArgs() [3]int {
	if len(os.Args) < 2 {
		help()
	}

	blockSize, err := strconv.Atoi(os.Args[1])
	if err != nil || (blockSize != 16 && blockSize != 32) {
		log.Fatalf("BlockSize is incorrect")
	}

	if len(os.Args) == 2 {
		return [3]int{blockSize, 0, 0}
	}

	if len(os.Args) != 4 {
		help()
	}

	iterationsBeforeTransform, err := strconv.Atoi(os.Args[2])
	if err != nil || iterationsBeforeTransform <= 0 {
		log.Fatalf("IterationsBeforeTransform is incorrect")
	}
	compressionIterations, err := strconv.Atoi(os.Args[3])
	if err != nil || compressionIterations <= 0 {
		log.Fatalf("CompressionIterations is incorrect")
	}
	return [3]int{blockSize, iterationsBeforeTransform, compressionIterations}
}

func main() {
	params := parseArgs()
	bytes, _ := io.ReadAll(os.Stdin)

	if params[1] == 0 && params[2] == 0 {
		if params[0] == 16 {
			fmt.Println(hex.EncodeToString(Hash128(bytes)))
		} else {
			fmt.Println(hex.EncodeToString(Hash256(bytes)))
		}
	} else {
		fmt.Println(hex.EncodeToString(HashExperimental(params[0], params[1], params[2], bytes)))
	}
}
