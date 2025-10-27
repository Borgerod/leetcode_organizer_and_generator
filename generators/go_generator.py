def generate_boilerplate(data, indent):
    """Generate Go-specific boilerplate code."""
    code_snippet = data['code_snippet']

    if '{\n    \n}' in code_snippet:
        if '*ListNode' in code_snippet or '*TreeNode' in code_snippet:
            return_value = 'nil'
        elif '[]' in code_snippet:
            return_value = 'nil'
        elif 'int' in code_snippet and 'func' in code_snippet and '*' not in code_snippet:
            return_value = '0'
        elif 'bool' in code_snippet:
            return_value = 'false'
        elif 'string' in code_snippet:
            return_value = '""'
        else:
            return_value = 'nil'
        code_content = code_snippet.replace('{\n    \n}', f'''{{
    /*
    
    */
    
    return {return_value}
}}''')
    else:
        code_content = f'''{code_snippet.rstrip()}
    /*
    
    */
    
    return nil
}}'''

    test_cases = data.get('test_cases', [])
    if test_cases and len(data['params']) <= 1:
        go_cases = [f'        {case}' for case in test_cases]
        test_array = ',\n'.join(go_cases)
        test_code = f"""    testCases := []interface{{}}{{
{test_array},
    }}
    
    for i, testCase := range testCases {{
        fmt.Printf(\"___ NO.%d ___________________________________\\n\", i)
        fmt.Printf(\"Input: %v\\n\", testCase)
        fmt.Printf(\"Output: %v\\n\", {data['function_name']}(testCase.(int)))
        fmt.Println()
    }}"""
    elif test_cases and len(data['params']) > 1:
        param_count = len(data['params'])
        go_cases = []
        for index in range(0, len(test_cases), param_count):
            case_group = test_cases[index:index + param_count]
            formatted_cases = []
            for case in case_group:
                if case.startswith('[') and case.endswith(']'):
                    inner = case[1:-1]
                    formatted_cases.append(f'[]int{{{inner}}}')
                else:
                    formatted_cases.append(case)
            go_case = ', '.join(formatted_cases)
            go_cases.append(f'        {{{go_case}}}')
        test_array = ',\n'.join(go_cases)
        if param_count == 2:
            param_names = 'testCase[0].([]int), testCase[1].(int)'
        else:
            param_names = ', '.join([f'testCase[{index}]' for index in range(param_count)])
        test_code = f"""    testCases := [][]interface{{}}{{
{test_array},
    }}
    
    for i, testCase := range testCases {{
        fmt.Printf(\"___ NO.%d ___________________________________\\n\", i)
        fmt.Printf(\"Input: %v\\n\", testCase)
        fmt.Printf(\"Output: %v\\n\", {data['function_name']}({param_names}))
        fmt.Println()
    }}"""
    else:
        test_code = f'''    // TODO: Add test cases
    fmt.Println("Go solution for: {data['title']}")'''

    full_code = f'''package main

import "fmt"

{code_content}

func main() {{
{test_code}
}}'''

    return full_code
