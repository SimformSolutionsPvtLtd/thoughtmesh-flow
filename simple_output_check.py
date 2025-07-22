import json

import requests


def check_outputs():
    try:
        response = requests.get("http://localhost:7860/api/v1/all?framework=agno", timeout=10)
        response.raise_for_status()
        data = response.json()

        print("=== AGNO OUTPUTS STRUCTURE CHECK ===")

        issues = []
        total_comps = 0
        total_outputs = 0

        for category, components in data.items():
            for comp_name, comp_data in components.items():
                total_comps += 1
                outputs = comp_data.get("outputs", [])
                total_outputs += len(outputs)

                print(f"{comp_name}: {len(outputs)} outputs")

                for i, output in enumerate(outputs):
                    if not isinstance(output, dict):
                        issue = f"{comp_name} output {i}: not a dict"
                        print(f"  ERROR: {issue}")
                        issues.append(issue)
                        continue

                    if "types" not in output:
                        issue = f"{comp_name} output {i}: missing types"
                        print(f"  ERROR: {issue}")
                        issues.append(issue)
                    elif output["types"] is None:
                        issue = f"{comp_name} output {i}: types is null"
                        print(f"  ERROR: {issue}")
                        issues.append(issue)
                    elif not isinstance(output["types"], list):
                        issue = f"{comp_name} output {i}: types not a list, it is: {type(output['types'])}"
                        print(f"  ERROR: {issue}")
                        issues.append(issue)
                    elif len(output["types"]) == 0:
                        issue = f"{comp_name} output {i}: empty types array"
                        print(f"  WARNING: {issue}")
                    else:
                        print(f"  output {i} OK: types={output['types']}")

        print(f"\nSUMMARY: {total_comps} components, {total_outputs} outputs, {len(issues)} issues")
        if issues:
            print("ISSUES:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("All outputs structure OK!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_outputs()
