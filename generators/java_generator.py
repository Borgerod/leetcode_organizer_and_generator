def generate_boilerplate(data, indent):
    """Generate Java-specific boilerplate code."""
    code_snippet = data['code_snippet']

    if 'boolean' in code_snippet:
        return_value = 'false'
    elif 'int' in code_snippet and 'int[]' not in code_snippet:
        return_value = '0'
    elif 'String' in code_snippet:
        return_value = '""'
    elif '[]' in code_snippet or 'List' in code_snippet:
        return_value = 'null'
    else:
        return_value = 'null'

    test_cases = data.get('test_cases', [])
    if test_cases:
        if len(data['params']) <= 1:
            java_cases = [f'            {case}' for case in test_cases]
            test_array = ',\n'.join(java_cases)
            test_code = f'''        String[] testCases = {{
{test_array}
        }};
        
        for (int i = 0; i < testCases.length; i++) {{
            System.out.println("___ NO." + i + " ___________________________________");
            System.out.println("Input: " + testCases[i]);
            System.out.println("Output: " + solution.{data['function_name']}(testCases[i]));
            System.out.println();
        }}'''
        else:
            param_count = len(data['params'])
            grouped_cases = []
            for index in range(0, len(test_cases), param_count):
                case_group = test_cases[index:index + param_count]
                formatted_cases = []
                for case in case_group:
                    if case.startswith('[') and case.endswith(']'):
                        inner = case[1:-1]
                        formatted_cases.append(f'new int[]{{{inner}}}')
                    else:
                        formatted_cases.append(case)
                java_case = ', '.join(formatted_cases)
                grouped_cases.append(f'            {{{java_case}}}')
            test_array = ',\n'.join(grouped_cases)
            param_list = ', '.join([f'(int[])testCases[i][{index}]' if index == 0 else f'(int)testCases[i][{index}]' for index in range(param_count)])
            test_code = f'''        Object[][] testCases = {{
{test_array}
        }};
        
        for (int i = 0; i < testCases.length; i++) {{
            System.out.println("___ NO." + i + " ___________________________________");
            System.out.println("Input: " + java.util.Arrays.toString((int[])testCases[i][0]) + ", " + testCases[i][1]);
            System.out.println("Output: " + java.util.Arrays.toString(solution.{data['function_name']}({param_list})));
            System.out.println();
        }}'''
    else:
        test_code = f'''        // TODO: Add test cases
        System.out.println("Java solution for: {data['title']}");'''

    if '{\n        \n    }' in code_snippet:
        code_content = code_snippet.replace('{\n        \n    }', f'''{{
        /*
        
        */
        
        return {return_value};
    }}
    
    public static void main(String[] args) {{
        Solution solution = new Solution();
        
{test_code}
    }}''')
    else:
        lines = code_snippet.split('\n')
        for index in range(len(lines) - 1, -1, -1):
            if lines[index].strip() == '}':
                insertion = f'    \n    public static void main(String[] args) {{\n        Solution solution = new Solution();\n        \n{test_code}\n    }}'
                lines.insert(index, insertion)
                break
        code_content = '\n'.join(lines)

    return code_content
