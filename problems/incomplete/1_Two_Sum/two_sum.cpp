#include <iostream>
#include <vector>
#include <string>
#include <utility>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        /*
        
        */
        
        return {};
    }
};

int main() {
    Solution solution;
    
    vector<pair<vector<int>, int>> testCases = {
        { vector<int>{2,7,11,15}, 9 },
        { vector<int>{3,2,4}, 6 },
        { vector<int>{3,3}, 6 }
    };
    
    for (int i = 0; i < static_cast<int>(testCases.size()); i++) {
        vector<int> nums = testCases[i].first;
        int target = testCases[i].second;
        vector<int> result = solution.twoSum(nums, target);
        cout << "___ NO." << i << " ___________________________________" << endl;
        cout << "Input: [";
        for (size_t j = 0; j < nums.size(); j++) {
            cout << nums[j];
            if (j + 1 < nums.size()) cout << ",";
        }
        cout << "], " << target << endl;
        cout << "Output: [";
        for (size_t j = 0; j < result.size(); j++) {
            cout << result[j];
            if (j + 1 < result.size()) cout << ",";
        }
        cout << "]" << endl << endl;
    }
    
    return 0;
}