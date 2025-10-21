class Solution {
    public int[] twoSum(int[] nums, int target) {
        /*
        
        */
        
        return null;
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        
        Object[][] testCases = {
            {new int[]{2,7,11,15}, 9},
            {new int[]{3,2,4}, 6},
            {new int[]{3,3}, 6}
        };
        
        for (int i = 0; i < testCases.length; i++) {
            System.out.println("___ NO." + i + " ___________________________________");
            System.out.println("Input: " + java.util.Arrays.toString((int[])testCases[i][0]) + ", " + testCases[i][1]);
            System.out.println("Output: " + java.util.Arrays.toString(solution.twoSum((int[])testCases[i][0], (int)testCases[i][1])));
            System.out.println();
        }
    }
}