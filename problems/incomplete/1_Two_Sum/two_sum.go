package main

import "fmt"

func twoSum(nums []int, target int) []int {
    /*
    
    */
    
    return nil
}

func main() {
    testCases := [][]interface{}{
        {[]int{2,7,11,15}, 9},
        {[]int{3,2,4}, 6},
        {[]int{3,3}, 6},
    }
    
    for i, testCase := range testCases {
        fmt.Printf("___ NO.%d ___________________________________\n", i)
        fmt.Printf("Input: %v\n", testCase)
        fmt.Printf("Output: %v\n", twoSum(testCase[0].([]int), testCase[1].(int)))
        fmt.Println()
    }
}