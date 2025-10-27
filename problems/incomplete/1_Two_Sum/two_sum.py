class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        
        '''
        
        '''



        return None



    

if __name__ == '__main__':

    cases = [
        [2,7,11,15],
		9,
		[3,2,4],
		6,
		[3,3],
		6
    ]

    #> OPTION 2 (for multiple inputs)
    s = Solution()
    for i in range(0, len(cases), 2):

        nums = cases[i+0]
        target = cases[i+1]
        print(f"___ NO.{i} ___________________________________")
        print(f"n={i} -> {s.twoSum(nums, target)}\n")



'''
(NEW) TESTCASES:
cases = [
    '[2,7,11,15]',
    '9',
    '[3,2,4]',
    '6',
    '[3,3]',
    '6',
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
    [1, 2, 3],
    0,
]

FOR LEETCODE:
'[2,7,11,15]'
'9'
'[3,2,4]'
'6'
'[3,3]'
'6'
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
[1, 2, 3]
0
'''


"""
__ GITHUB PUSH COMMENT _________________________
Finish 1. Two Sum + move to completed
contains: description, solution.
difficulty: Easy
topics: Array, Hash Table
"""