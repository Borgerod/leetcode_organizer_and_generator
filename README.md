# LeetCode Organizer & Generator

Utility scripts for downloading LeetCode problem statements and scaffolding language-specific starter files.

## TODO:

-       Make generator for extra testcases
-       Make generator for git push description.

## Overview

-   Fetch problem metadata via LeetCode's GraphQL API
-   Generate boilerplate solutions in five languages: Python, JavaScript, Go, Java, and C++
-   Populate working test harnesses for every supported language
-   Organize output inside `problems/` under `completed/` and `incomplete/`

This tutorial walks through setup, configuration, and daily usage.

## 1. Prerequisites

1. **Python 3.10+** installed and available on your PATH
2. **Pip packages**: `requests` and `beautifulsoup4`
    ```powershell
    pip install requests beautifulsoup4
    ```
3. **LeetCode account** (anonymous access works for free problems, but Locked problems require an authenticated account)

## 2. Configure Your Preferred Language

The generator respects the simple `settings.INI` file in the project root.

```ini
language = python
```

Accepted values (`case-insensitive`):

| Value               | Output File Extension                    |
| ------------------- | ---------------------------------------- |
| `python`            | `.py`                                    |
| `javascript` / `js` | `.js`                                    |
| `go`                | `.go`                                    |
| `java`              | `.java`                                  |
| `c++`               | `.cpp` (auto-mapped internally to `cpp`) |

> **Tip:** Update the language whenever you switch stacks. The script reads the file on every run—no restart required.

## 3. Generate a Problem

Run the generator with the problem slug you want. Use the slug from the LeetCode URL (e.g., `two-sum`).

```powershell
python leetcode_problem_generator.py two-sum
```

What happens:

1. **Fetch problem data** (title, difficulty, description, tags)
2. **Download the official code snippet** for your configured language
3. **Parse function signatures** and example test cases
4. **Create an organized folder** under `problems/incomplete/<id>_<slug>/`
5. **Write language-specific boilerplate** with runnable test harnesses

If a folder already exists, the script updates its contents but never overwrites handwritten solutions. Move a finished solution into `problems/completed/` to keep your workspace clean.

## 4. Example Output Structure

After running the `two-sum` example for Go (`language = go`):

```
problems/
	incomplete/
		1_Two_Sum/
			description.txt      # Cleaned markdown problem statement
			two_sum.go           # Go boilerplate + tests ready to run
```

All languages follow the same pattern:

-   **Description files** capture the formatted question text
-   **Solution files** contain a stub inside the main function/class plus a test loop that exercises the example cases

## 5. Working With the Generated Files

-   **Implement the solution** inside the generated function/method
-   **Run the bundled tests** (each language’s main/test harness echoes inputs and outputs)
-   **Move solved problems** to `problems/completed/` to track progress

### Language Notes

-   **Python**: Uses `if __name__ == "__main__"` with simple loops over inputs
-   **JavaScript**: Logs each case with `console.log`
-   **Go**: Generates strongly typed slices and asserts parameter types
-   **Java**: Builds `Object[][]` arrays, casts to the expected parameter types, and prints using `Arrays.toString`
-   **C++**: Stores cases in `std::vector<std::pair<...>>` and prints via helper loops

## 6. Troubleshooting

| Issue                                  | Fix                                                                                        |
| -------------------------------------- | ------------------------------------------------------------------------------------------ |
| `Warning: Could not read settings.INI` | Ensure the file is UTF-8 encoded and contains a valid `language = value` line              |
| Test harness prints unexpected types   | Double-check the language selection; generated stubs match the signature for that language |
| Locked problem fetch fails             | Sign in to LeetCode in a browser before running, or avoid locked questions                 |
| Need to re-run after language change   | Update `settings.INI` and run the script again—the tool re-fetches code snippets           |

## 7. Contributing & Customization

-   Add new language generators by following the existing patterns in `leetcode_problem_generator.py`
-   Extend the test harness logic or post-processing as desired (e.g., auto-formatting, linting)
-   Pull requests welcome for additional features or bug fixes

---

Happy grinding, and enjoy the consistency of a well-organized LeetCode workspace!
