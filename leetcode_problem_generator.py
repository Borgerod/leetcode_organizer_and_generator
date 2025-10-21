import os
import re
import sys
import json
import requests
import configparser
from html.parser import HTMLParser

class HTMLFilter(HTMLParser):
    """Remove HTML tags from description"""
    text = ""
    def handle_data(self, data):
        self.text += data
    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.text += '\n'
        elif tag in ['p', 'div']:
            self.text += '\n'
    def handle_endtag(self, tag):
        if tag in ['p', 'div']:
            self.text += '\n'

def clean_html(html_text):
    """Remove HTML tags from description and format nicely"""
    f = HTMLFilter()
    f.feed(html_text)
    text = f.text.strip()
    
    # Clean up excessive whitespace and format properly
    lines = text.split('\n')
    formatted_lines = []
    in_example = False
    in_constraints = False
    
    def wrap_text(text, width=100, indent_level=0):
        """Wrap text to specified width with optional indentation"""
        if not text.strip():
            return ['']
        
        words = text.split()
        lines = []
        current_line = ''
        indent = '    ' * indent_level
        
        for word in words:
            # Check if adding this word would exceed the width
            test_line = current_line + (' ' if current_line else '') + word
            if len(indent + test_line) <= width:
                current_line = test_line
            else:
                # Start a new line
                if current_line:
                    lines.append(indent + current_line)
                current_line = word
        
        # Add the last line
        if current_line:
            lines.append(indent + current_line)
        
        return lines if lines else ['']
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:  # Empty line
            formatted_lines.append('')
            continue
            
        # Check if we're starting an example or constraints section
        if line.startswith('Example ') and line.endswith(':'):
            in_example = True
            in_constraints = False
            formatted_lines.append(line)
            continue
        elif line.lower().startswith('constraint') and ':' in line:
            in_example = False
            in_constraints = True
            formatted_lines.append(line)
            continue
            
        # Handle Input/Output/Explanation lines (always indent these)
        if line.startswith(('Input:', 'Output:', 'Explanation:')):
            formatted_lines.append(f'    {line}')
            continue
            
        # Skip pure number lines
        if line.replace(' ', '').replace('\t', '').isdigit():
            continue
            
        # Handle content based on current section
        if in_example:
            # In example section - indent everything except the Example X: header
            if not (line.startswith('Example ') and line.endswith(':')):
                # For example content, wrap with 1 level of indentation
                wrapped = wrap_text(line, width=100, indent_level=1)
                formatted_lines.extend(wrapped)
            else:
                formatted_lines.append(line)
        elif in_constraints:
            # In constraints section - indent all constraint details
            wrapped = wrap_text(line, width=100, indent_level=1)
            formatted_lines.extend(wrapped)
        else:
            # Regular content outside examples/constraints - wrap to full width
            wrapped = wrap_text(line, width=100, indent_level=0)
            formatted_lines.extend(wrapped)
    
    # Remove excessive empty lines (max 1 consecutive for cleaner look)
    final_lines = []
    empty_count = 0
    
    for line in formatted_lines:
        if not line.strip():
            empty_count += 1
            if empty_count <= 1:  # Only allow 1 consecutive empty line
                final_lines.append(line)
        else:
            empty_count = 0
            final_lines.append(line)
    
    return '\n'.join(final_lines)

def read_settings():
    """Read preferred language from settings.INI file"""
    settings = {
        'language': 'python'  # Default to python
    }
    
    settings_path = 'settings.INI'
    if os.path.exists(settings_path):
        try:
            # Read the file manually to handle simple key=value format
            # Try UTF-8 first, then UTF-16 if that fails
            try:
                with open(settings_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(settings_path, 'r', encoding='utf-16') as f:
                    content = f.read()
            
            for line in content.split('\n'):
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith('#') or not line or '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'language':
                    lang_value = value.lower()
                    # Handle c++ alias
                    if lang_value == 'c++':
                        lang_value = 'cpp'
                    settings['language'] = lang_value
                        
        except Exception as e:
            print(f"Warning: Could not read settings.INI: {e}")
            print("Using default language: python")
    
    return settings

def get_vscode_settings():
    """Get VS Code indentation settings"""
    settings = {
        'insert_spaces': True,  # Default to spaces
        'tab_size': 4,         # Default to 4 spaces
        'indent_string': '    ' # Default indent
    }
    
    # Try to read workspace settings first
    workspace_settings_path = os.path.join('.vscode', 'settings.json')
    user_settings_path = os.path.expanduser('~/AppData/Roaming/Code/User/settings.json')
    
    def read_settings_file(path):
        """Read and parse settings JSON file"""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove comments (simple approach)
                    lines = content.split('\n')
                    clean_lines = []
                    for line in lines:
                        # Remove // comments
                        if '//' in line:
                            line = line[:line.index('//')]
                        clean_lines.append(line)
                    clean_content = '\n'.join(clean_lines)
                    return json.loads(clean_content)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            pass
        return {}
    
    # Read workspace settings (takes priority)
    workspace_settings = read_settings_file(workspace_settings_path)
    
    # Read user settings (fallback)
    user_settings = read_settings_file(user_settings_path)
    
    # Merge settings (workspace overrides user)
    all_settings = {**user_settings, **workspace_settings}
    
    # Extract relevant settings
    if 'editor.insertSpaces' in all_settings:
        settings['insert_spaces'] = all_settings['editor.insertSpaces']
    
    if 'editor.tabSize' in all_settings:
        settings['tab_size'] = all_settings['editor.tabSize']
    
    # Check for Python-specific settings
    python_settings = all_settings.get('[python]', {})
    if 'editor.insertSpaces' in python_settings:
        settings['insert_spaces'] = python_settings['editor.insertSpaces']
    if 'editor.tabSize' in python_settings:
        settings['tab_size'] = python_settings['editor.tabSize']
    
    # Create indent string
    if settings['insert_spaces']:
        settings['indent_string'] = ' ' * settings['tab_size']
    else:
        settings['indent_string'] = '\t'
    
    return settings

def fetch_leetcode_problem(problem_slug, preferred_language='python'):
    """Fetch problem data using LeetCode's GraphQL API"""
    
    # Map settings language to LeetCode API language names
    language_map = {
        'python': 'Python3',
        'java': 'Java',
        'cpp': 'C++',
        'javascript': 'JavaScript',
        'go': 'Go'
    }
    
    leetcode_lang = language_map.get(preferred_language.lower(), 'Python3')
    
    url = "https://leetcode.com/graphql"
    
    # GraphQL query
    query = """
    query getQuestionDetail($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            title
            titleSlug
            difficulty
            content
            topicTags {
                name
                slug
            }
            codeSnippets {
                lang
                code
            }
            exampleTestcases
        }
    }
    """
    
    variables = {"titleSlug": problem_slug}
    
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com"
    }
    
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            print(f"API Error: {data['errors']}")
            return None
            
        question = data['data']['question']
        
        # Get code snippet for preferred language
        target_code = None
        for snippet in question['codeSnippets']:
            if snippet['lang'] == leetcode_lang:
                target_code = snippet['code']
                break
        
        if not target_code:
            print(f"No {leetcode_lang} code snippet found")
            return None
        
        # For Python: Fix capitalized types (List[str] -> list[str])
        if preferred_language.lower() == 'python':
            target_code = re.sub(r'\bList\[', 'list[', target_code)
            target_code = re.sub(r'\bDict\[', 'dict[', target_code)
            target_code = re.sub(r'\bSet\[', 'set[', target_code)
            target_code = re.sub(r'\bTuple\[', 'tuple[', target_code)
        
        # Parse function signature based on language
        function_name = "INSERT_FUNCTION_NAME"
        params = []
        
        if preferred_language.lower() == 'python':
            func_match = re.search(r'def\s+(\w+)\s*\(self(?:,\s*(.+?))?\)\s*->', target_code, re.DOTALL)
            if func_match:
                function_name = func_match.group(1)
                if func_match.group(2):
                    param_text = func_match.group(2)
                    for param in param_text.split(','):
                        param_name = param.split(':')[0].strip()
                        if param_name and param_name != 'self':
                            params.append(param_name)
        
        elif preferred_language.lower() == 'javascript':
            # JavaScript: var functionName = function(param1, param2) {
            func_match = re.search(r'var\s+(\w+)\s*=\s*function\s*\(([^)]*)\)', target_code)
            if func_match:
                function_name = func_match.group(1)
                if func_match.group(2).strip():
                    param_text = func_match.group(2)
                    for param in param_text.split(','):
                        param_name = param.strip()
                        if param_name:
                            params.append(param_name)
        
        elif preferred_language.lower() == 'java':
            # Java: public returnType functionName(Type param1, Type param2) {
            # Updated to handle array return types like int[]
            func_match = re.search(r'public\s+\w+(?:\[\])?\s+(\w+)\s*\(([^)]*)\)', target_code)
            if func_match:
                function_name = func_match.group(1)
                if func_match.group(2).strip():
                    param_text = func_match.group(2)
                    for param in param_text.split(','):
                        param_parts = param.strip().split()
                        if len(param_parts) >= 2:
                            params.append(param_parts[-1])  # Last part is parameter name
        
        elif preferred_language.lower() == 'cpp':
            # C++: Look for method signature in class (returnType functionName(params))
            func_match = re.search(r'(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)', target_code)
            if func_match:
                function_name = func_match.group(2)  # Second group is function name
                if func_match.group(3).strip():
                    param_text = func_match.group(3)
                    for param in param_text.split(','):
                        param_parts = param.strip().split()
                        if len(param_parts) >= 2:
                            # Remove & and * from parameter names
                            param_name = param_parts[-1].replace('&', '').replace('*', '')
                            params.append(param_name)
        
        elif preferred_language.lower() == 'go':
            # Go: func functionName(param1 type1, param2 type2) returnType {
            func_match = re.search(r'func\s+(\w+)\s*\(([^)]*)\)', target_code)
            if func_match:
                function_name = func_match.group(1)
                if func_match.group(2).strip():
                    param_text = func_match.group(2)
                    for param in param_text.split(','):
                        param_parts = param.strip().split()
                        if len(param_parts) >= 2:
                            params.append(param_parts[0])  # First part is parameter name in Go
        
        # Parse test cases
        test_cases = question['exampleTestcases'].split('\n') if question['exampleTestcases'] else []
        
        return {
            'number': question['questionFrontendId'],
            'title': f"{question['questionFrontendId']}. {question['title']}",
            'difficulty': question['difficulty'],
            'topics': [tag['name'] for tag in question['topicTags']],
            'description': question['content'],
            'function_name': function_name,
            'params': params,
            'test_cases': test_cases,
            'code_snippet': target_code,
            'language': preferred_language
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def create_files(data):
    """Create folder structure and files with API data"""
    
    # Get VS Code indentation settings
    vscode_settings = get_vscode_settings()
    indent = vscode_settings['indent_string']
    
    # Get file extension based on language
    language = data.get('language', 'python').lower()
    extension_map = {
        'python': '.py',
        'java': '.java',
        'cpp': '.cpp',
        'javascript': '.js',
        'go': '.go'
    }
    file_extension = extension_map.get(language, '.py')
    
    print(f"Using language: {language}")
    print(f"Using indentation: {'spaces' if vscode_settings['insert_spaces'] else 'tabs'} "
          f"(size: {vscode_settings['tab_size']})")
    
    # Create folder name: "2942_Find_Words_Containing_Character"
    folder_name = data['title'].replace(' ', '_').replace('.', '')
    
    # Create file name with appropriate extension
    title_without_number = re.sub(r'^\d+\s*\.?\s*', '', data['title'])
    file_name = title_without_number.replace(' ', '_').lower() + file_extension
    
    # Create folder path
    base_path = os.path.join('problems', 'incomplete', folder_name)
    os.makedirs(base_path, exist_ok=True)
    
    # Create description.txt
    desc_path = os.path.join(base_path, 'description.txt')
    
    # Create matching underlines
    title_line = f"___ {data['title']} "
    total_width = 100  # Target total width
    remaining_width = total_width - len(title_line)
    title_underline = '_' * max(0, remaining_width)
    bottom_underline = '_' * total_width
    
    desc_content = f"""{title_line}{title_underline}
difficulty: {data['difficulty']}
topics: {', '.join(data['topics'])}
{bottom_underline}


{clean_html(data['description'])}
"""
    
    with open(desc_path, 'w', encoding='utf-8') as f:
        f.write(desc_content)
    
    # Create code file with language-specific content
    code_path = os.path.join(base_path, file_name)
    
    # Generate language-specific boilerplate
    if language == 'python':
        code_content = generate_python_boilerplate(data, indent)
    elif language == 'javascript':
        code_content = generate_javascript_boilerplate(data, indent)
    elif language == 'java':
        code_content = generate_java_boilerplate(data, indent)
    elif language == 'cpp':
        code_content = generate_cpp_boilerplate(data, indent)
    elif language == 'go':
        code_content = generate_go_boilerplate(data, indent)
    else:
        # Fallback to basic template
        code_content = f"{data['code_snippet']}\n\n// TODO: Add test cases and main function"
    
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code_content)
    
    print(f"✓ Created folder: {folder_name}")
    print(f"✓ Created files:")
    print(f"  - {desc_path}")
    print(f"  - {code_path}")
    print(f"\nTitle: {data['title']}")
    print(f"Difficulty: {data['difficulty']}")
    print(f"Topics: {', '.join(data['topics'])}")
    print(f"Function: {data['function_name']}")
    print(f"Parameters: {', '.join(data['params'])}")
    
    return base_path

def generate_python_boilerplate(data, indent):
    """Generate Python-specific boilerplate code"""
    # Build test cases string
    cases_str = ',\n\t\t'.join([f'{case}' for case in data['test_cases']])
    if not cases_str:
        cases_str = '"TESTCASE"'
    
    # Choose boilerplate based on number of parameters
    if len(data['params']) <= 1:
        param_name = data['params'][0] if data['params'] else 'PARAM'
        bottom_boilerplate = f'''
{indent}#> OPTION 1 (for single inputs)
{indent}s = Solution()
{indent}for i, {param_name} in enumerate(cases):
{indent}{indent}print(f"___ NO.{{i}} ___________________________________")
{indent}{indent}print(f"n={{i}} -> {{s.{data['function_name']}({param_name})}}\\n")
'''
    else:
        param_list = ', '.join(data['params'])
        bottom_boilerplate = f'''
{indent}#> OPTION 2 (for multiple inputs)
{indent}s = Solution()
{indent}for i in range(0, len(cases), {len(data['params'])}):
'''
        for j, param in enumerate(data['params']):
            bottom_boilerplate += f'\n{indent}{indent}{param} = cases[i+{j}]'
        bottom_boilerplate += f'''
{indent}{indent}print(f"___ NO.{{i}} ___________________________________")
{indent}{indent}print(f"n={{i}} -> {{s.{data['function_name']}({param_list})}}\\n")
'''
    
    return f'''{data['code_snippet']}
{indent}{indent}\'\'\'
{indent}{indent}
{indent}{indent}\'\'\'



{indent}{indent}return None



{indent}

if __name__ == '__main__':

{indent}cases = [
{indent}{indent}{cases_str}
{indent}]
{bottom_boilerplate}
'''

def generate_javascript_boilerplate(data, indent):
    """Generate JavaScript-specific boilerplate code"""
    # Build test cases string for JavaScript
    test_cases = data.get('test_cases', [])
    
    # Simply replace the function body content between the braces
    code_snippet = data['code_snippet']
    
    # Replace the empty function body with our boilerplate
    # The snippet ends with something like "{\n    \n};" so we replace the middle part
    if '{\n    \n};' in code_snippet:
        code_content = code_snippet.replace('{\n    \n};', '''{\n    /*\n    \n    */\n    \n    return null;\n};''')
    elif '{\n    \n}' in code_snippet:
        code_content = code_snippet.replace('{\n    \n}', '''{\n    /*\n    \n    */\n    \n    return null;\n}''')
    else:
        # Fallback - just append our code
        code_content = f'''{code_snippet}
    /*
    
    */
    
    return null;
}}'''
    
    # Build test cases
    if test_cases:
        if len(data['params']) <= 1:
            # Single parameter
            cases_str = ',\n    '.join([f'{case}' for case in test_cases])
            test_code = f'''
// Test cases
const cases = [
    {cases_str}
];

// Run tests
cases.forEach((testCase, i) => {{
    console.log(`___ NO.${{i}} ___________________________________`);
    console.log(`Input: ${{testCase}}`);
    console.log(`Output: ${{{data['function_name']}(testCase)}}`);
    console.log();
}});'''
        else:
            # Multiple parameters
            param_count = len(data['params'])
            cases_str = ',\n    '.join([f'{case}' for case in test_cases])
            param_list = ', '.join(data['params'])
            test_code = f'''
// Test cases (multiple parameters)
const cases = [
    {cases_str}
];

// Run tests
for (let i = 0; i < cases.length; i += {param_count}) {{
'''
            for j, param in enumerate(data['params']):
                test_code += f'    const {param} = cases[i + {j}];\n'
            test_code += f'''    console.log(`___ NO.${{i}} ___________________________________`);
    console.log(`Input: ${{[{param_list}]}}`);
    console.log(`Output: ${{{data['function_name']}({param_list})}}`);
    console.log();
}}'''
    else:
        test_code = f'''
// TODO: Add test cases
console.log("JavaScript solution for: {data['title']}");'''
    
    return code_content + test_code

def generate_java_boilerplate(data, indent):
    """Generate Java-specific boilerplate code"""
    # Java code snippet should be complete, just add our boilerplate inside the method
    code_snippet = data['code_snippet']
    
    # Determine return value based on method signature
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
    
    # Build test cases for Java
    test_cases = data.get('test_cases', [])
    if test_cases:
        # Build test cases array
        java_cases = []
        if len(data['params']) <= 1:
            # Single parameter
            for case in test_cases:
                java_cases.append(f'            {case}')
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
            # Multiple parameters - group by parameter count
            param_count = len(data['params'])
            grouped_cases = []
            for i in range(0, len(test_cases), param_count):
                case_group = test_cases[i:i + param_count]
                formatted_cases = []
                for case in case_group:
                    # Convert Python/LeetCode array syntax to Java syntax
                    if case.startswith('[') and case.endswith(']'):
                        # Convert [2,7,11,15] to new int[]{2,7,11,15}
                        inner = case[1:-1]  # Remove [ and ]
                        formatted_case = f'new int[]{{{inner}}}'
                        formatted_cases.append(formatted_case)
                    else:
                        formatted_cases.append(case)
                java_case = ', '.join(formatted_cases)
                grouped_cases.append(f'            {{{java_case}}}')
            test_array = ',\n'.join(grouped_cases)
            param_list = ', '.join([f'(int[])testCases[i][{j}]' if j == 0 else f'(int)testCases[i][{j}]' for j in range(param_count)])
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
        test_code = '''        // TODO: Add test cases
        System.out.println("Java solution for: " + "''' + data['title'] + '''");'''
    
    # Replace the empty method body with our boilerplate
    if '{\n        \n    }' in code_snippet:
        # Replace the method body and add main method inside the class
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
        # Fallback - add method body and main method
        lines = code_snippet.split('\n')
        # Find the last } and insert main method before it
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == '}':
                lines.insert(i, f'    \n    public static void main(String[] args) {{\n        Solution solution = new Solution();\n        \n{test_code}\n    }}')
                break
        code_content = '\n'.join(lines)
    
    return code_content

def generate_cpp_boilerplate(data, indent):
    """Generate C++-specific boilerplate code"""
    # C++ code snippet should be complete, just add our boilerplate inside the method
    code_snippet = data['code_snippet']
    
    # Replace the empty method body with our boilerplate
    if '{\n        \n    }' in code_snippet:
        code_content = code_snippet.replace('{\n        \n    }', '''{\n        /*\n        \n        */\n        \n        return {};\n    }''')
    elif '{\n        \n}' in code_snippet:
        code_content = code_snippet.replace('{\n        \n}', '''{\n        /*\n        \n        */\n        \n        return {};\n    }''')
    else:
        # Fallback - assume it ends with opening brace
        code_content = code_snippet.rstrip() + '''
        /*
        
        */
        
        return {};
    }'''
    
    # Build test cases for C++
    test_cases = data.get('test_cases', [])
    function_name = data.get('function_name', 'solution')
    
    # Special handling for Two Sum regardless of parameter count
    if 'two' in data['title'].lower() and 'sum' in data['title'].lower():
        # Use actual fetched test cases instead of hardcoded ones
        if test_cases and len(test_cases) >= 2:
            # Parse test cases in pairs (array, target)
            cpp_test_cases = []
            for i in range(0, len(test_cases), 2):
                if i + 1 < len(test_cases):
                    array_case = test_cases[i]
                    target_case = test_cases[i + 1]
                    if array_case.startswith('[') and array_case.endswith(']'):
                        inner_values = array_case[1:-1]
                    else:
                        inner_values = array_case
                    vector_expr = f'vector<int>{{{inner_values}}}' if inner_values else 'vector<int>{}'
                    cpp_test_cases.append((vector_expr, target_case))
            
            if cpp_test_cases:
                case_entries = []
                for vector_expr, target in cpp_test_cases:
                    case_entries.append(f'        {{ {vector_expr}, {target} }}')
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
            # Fallback if no test cases
            test_code = f'''    // No test cases available
    cout << "C++ solution for: {data['title']}" << endl;'''
    elif test_cases and len(data['params']) <= 1:
        # Single parameter - determine type from function signature
        code_snippet = data['code_snippet']
        cpp_cases = []
        
        # Determine parameter type from function signature
        if 'int' in code_snippet and '[]' not in code_snippet:
            # Function takes int parameter
            vector_type = 'vector<int>'
            for case in test_cases:
                cpp_cases.append(f'        {case}')
        elif 'string' in code_snippet:
            # Function takes string parameter  
            vector_type = 'vector<string>'
            for case in test_cases:
                cpp_cases.append(f'        "{case}"')
        elif 'bool' in code_snippet:
            # Function takes bool parameter
            vector_type = 'vector<bool>'
            for case in test_cases:
                cpp_cases.append(f'        {case}')
        else:
            # Default to string for unknown types
            vector_type = 'vector<string>'
            for case in test_cases:
                if isinstance(case, list):
                    # Convert Python list to C++ vector syntax
                    vector_str = '{' + ', '.join(str(x) for x in case) + '}'
                    cpp_cases.append(f'        vector<int>{vector_str}')
                else:
                    cpp_cases.append(f'        {case}')
        
        # Generic single parameter handling
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
        # Multiple parameters - for now, simplified approach
        test_code = f'''    // Multiple parameter test cases
    // TODO: Add specific test cases for multiple parameters
    cout << "C++ solution for: {data['title']}" << endl;'''
    else:
        test_code = f'''    // TODO: Add test cases
    cout << "C++ solution for: {data['title']}" << endl;'''
    
    # Add includes, namespace, and main function
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

def generate_go_boilerplate(data, indent):
    """Generate Go-specific boilerplate code"""
    # Go code snippet should be complete, just add our boilerplate inside the function
    code_snippet = data['code_snippet']
    
    # Replace the empty function body with our boilerplate
    # Need to determine proper return value based on return type
    if '{\n    \n}' in code_snippet:
        # Determine return value based on function signature
        if '*ListNode' in code_snippet or '*TreeNode' in code_snippet:
            return_value = 'nil'
        elif '[]' in code_snippet:  # slice/array - check this before int
            return_value = 'nil'
        elif 'int' in code_snippet and 'func' in code_snippet and '*' not in code_snippet:
            return_value = '0'
        elif 'bool' in code_snippet:
            return_value = 'false'
        elif 'string' in code_snippet:
            return_value = '""'
        else:
            return_value = 'nil'
            
        code_content = code_snippet.replace('{\n    \n}', f'{{\n    /*\n    \n    */\n    \n    return {return_value}\n}}')
    else:
        # Fallback - assume it ends with opening brace
        code_content = code_snippet.rstrip() + '''
    /*
    
    */
    
    return nil
}'''
    
    # Build test cases for Go  
    test_cases = data.get('test_cases', [])
    if test_cases and len(data['params']) <= 1:
        # Single parameter
        go_cases = []
        for case in test_cases:
            go_cases.append(f'        {case}')
        test_array = ',\n'.join(go_cases)
        test_code = f"""    testCases := []interface{{}}{{
{test_array},
    }}
    
    for i, testCase := range testCases {{
        fmt.Printf("___ NO.%d ___________________________________\\n", i)
        fmt.Printf("Input: %v\\n", testCase)
        fmt.Printf("Output: %v\\n", {data['function_name']}(testCase.(int)))
        fmt.Println()
    }}"""
    elif test_cases and len(data['params']) > 1:
        # Multiple parameters
        param_count = len(data['params'])
        go_cases = []
        for i in range(0, len(test_cases), param_count):
            case_group = test_cases[i:i + param_count]
            formatted_cases = []
            for case in case_group:
                # Convert Python/LeetCode array syntax to Go syntax
                if case.startswith('[') and case.endswith(']'):
                    # Convert [2,7,11,15] to []int{2,7,11,15}
                    inner = case[1:-1]  # Remove [ and ]
                    formatted_case = f'[]int{{{inner}}}'
                    formatted_cases.append(formatted_case)
                else:
                    formatted_cases.append(case)
            go_case = ', '.join(formatted_cases)
            go_cases.append(f'        {{{go_case}}}')
        test_array = ',\n'.join(go_cases)
        # Create proper type assertions for parameters
        if param_count == 2:
            # For two parameters like twoSum([]int, int)
            param_names = 'testCase[0].([]int), testCase[1].(int)'
        else:
            # Generic fallback
            param_names = ', '.join([f'testCase[{j}]' for j in range(param_count)])
        test_code = f"""    testCases := [][]interface{{}}{{
{test_array},
    }}
    
    for i, testCase := range testCases {{
        fmt.Printf("___ NO.%d ___________________________________\\n", i)
        fmt.Printf("Input: %v\\n", testCase)
        fmt.Printf("Output: %v\\n", {data['function_name']}({param_names}))
        fmt.Println()
    }}"""
    else:
        test_code = f'''    // TODO: Add test cases
    fmt.Println("Go solution for: {data['title']}")'''
    
    # Add main function and package
    full_code = f'''package main

import "fmt"

{code_content}

func main() {{
{test_code}
}}'''
    
    return full_code

if __name__ == '__main__':
    # Read settings first
    settings = read_settings()
    preferred_language = settings['language']
    
    print(f"Using preferred language: {preferred_language}")
    
    if len(sys.argv) < 2:
        url_or_slug = input("Enter LeetCode problem URL or slug: ")
    else:
        url_or_slug = sys.argv[1]
    
    # Extract slug from URL if needed
    if 'leetcode.com' in url_or_slug:
        slug_match = re.search(r'/problems/([^/]+)', url_or_slug)
        problem_slug = slug_match.group(1) if slug_match else url_or_slug
    else:
        problem_slug = url_or_slug
    
    print(f"Fetching problem: {problem_slug}...")
    data = fetch_leetcode_problem(problem_slug, preferred_language)
    
    if data:
        base_path = create_files(data)
        print(f"\nFolder succsessfully generated!\n    Folder is located at: {base_path}\n")
    else:
        print("Failed to fetch problem data")