def generate_boilerplate(data, indent):
    """Generate C++-specific boilerplate code."""
    code_snippet = data['code_snippet']

    if '{\n        \n    }' in code_snippet:
        code_content = code_snippet.replace('{\n        \n    }', '''{\n        /*\n        \n        */\n        \n        return {};\n    }''')
    elif '{\n        \n}' in code_snippet:
        code_content = code_snippet.replace('{\n        \n}', '''{\n        /*\n        \n        */\n        \n        return {};\n    }''')
    else:
        code_content = code_snippet.rstrip() + '''
        /*
        
        */
        
        return {};
    }'''

    test_cases = data.get('test_cases', [])
    function_name = data.get('function_name', 'solution')

    if 'two' in data['title'].lower() and 'sum' in data['title'].lower():
        if test_cases and len(test_cases) >= 2:
            cpp_test_cases = []
            for index in range(0, len(test_cases), 2):
                if index + 1 < len(test_cases):
                    array_case = test_cases[index]
                    target_case = test_cases[index + 1]
                    inner_values = array_case[1:-1] if array_case.startswith('[') and array_case.endswith(']') else array_case
                    vector_expr = f'vector<int>{{{inner_values}}}' if inner_values else 'vector<int>{}'
                    cpp_test_cases.append((vector_expr, target_case))
            if cpp_test_cases:
                case_entries = [f'        {{ {vector_expr}, {target} }}' for vector_expr, target in cpp_test_cases]
                cases_str = ',\n'.join(case_entries)
                test_code = f'''    vector<pair<vector<int>, int>> testCases = {{
{cases_str}
    }};
    
    for (int i = 0; i < static_cast<int>(testCases.size()); i++) {{
        vector<int> nums = testCases[i].first;
        int target = testCases[i].second;
        vector<int> result = solution.{function_name}(nums, target);
        cout << "___ NO." << i << " ___________________________________" << endl;
        cout << "Input: [";
        for (size_t j = 0; j < nums.size(); j++) {{
            cout << nums[j];
            if (j + 1 < nums.size()) cout << ",";
        }}
        cout << "], " << target << endl;
        cout << "Output: [";
        for (size_t j = 0; j < result.size(); j++) {{
            cout << result[j];
            if (j + 1 < result.size()) cout << ",";
        }}
        cout << "]" << endl << endl;
    }}'''
            else:
                test_code = f'''    // No test cases available
    cout << "C++ solution for: {data['title']}" << endl;'''
        else:
            test_code = f'''    // No test cases available
    cout << "C++ solution for: {data['title']}" << endl;'''
    elif test_cases and len(data['params']) <= 1:
        cpp_cases = []
        if 'int' in code_snippet and '[]' not in code_snippet:
            vector_type = 'vector<int>'
            cpp_cases = [f'        {case}' for case in test_cases]
        elif 'string' in code_snippet:
            vector_type = 'vector<string>'
            cpp_cases = [f'        "{case}"' for case in test_cases]
        elif 'bool' in code_snippet:
            vector_type = 'vector<bool>'
            cpp_cases = [f'        {case}' for case in test_cases]
        else:
            vector_type = 'vector<string>'
            for case in test_cases:
                if isinstance(case, list):
                    vector_str = '{' + ', '.join(str(value) for value in case) + '}'
                    cpp_cases.append(f'        vector<int>{vector_str}')
                else:
                    cpp_cases.append(f'        {case}')
        test_array = ',\n'.join(cpp_cases)
        test_code = f'''    {vector_type} testCases = {{
{test_array}
    }};
    
    for (int i = 0; i < testCases.size(); i++) {{
        cout << "___ NO." << i << " ___________________________________" << endl;
        cout << "Input: " << testCases[i] << endl;
        cout << "Output: " << solution.{function_name}(testCases[i]) << endl;
        cout << endl;
    }}'''
    elif test_cases and len(data['params']) > 1:
        test_code = f'''    // Multiple parameter test cases
    // TODO: Add specific test cases for multiple parameters
    cout << "C++ solution for: {data['title']}" << endl;'''
    else:
        test_code = f'''    // TODO: Add test cases
    cout << "C++ solution for: {data['title']}" << endl;'''

    full_code = f'''#include <iostream>
#include <vector>
#include <string>
#include <utility>
using namespace std;

{code_content}

int main() {{
    Solution solution;
    
{test_code}
    
    return 0;
}}'''

    return full_code
