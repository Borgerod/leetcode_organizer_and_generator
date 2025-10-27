def generate_boilerplate(data, indent):
    """Generate Python-specific boilerplate code."""
    cases_str = ',\n\t\t'.join([f'{case}' for case in data['test_cases']])
    if not cases_str:
        cases_str = '"TESTCASE"'

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
        for index, param in enumerate(data['params']):
            bottom_boilerplate += f'\n{indent}{indent}{param} = cases[i+{index}]'
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
