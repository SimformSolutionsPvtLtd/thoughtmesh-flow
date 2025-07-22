#!/usr/bin/env python3

import json

import requests


def test_outputs_structure():
    """Test the structure of outputs in the API response"""
    try:
        # Get Agno components
        print("Fetching Agno components...")
        response = requests.get("http://localhost:7860/api/v1/all?framework=agno")
        response.raise_for_status()
        agno_data = response.json()

        print("Checking Agno component outputs structure:")
        print("=" * 60)

        issues_found = []
        total_components = 0
        total_outputs = 0

        for category, components in agno_data.items():
            print(f"\nCategory: {category}")
            for comp_name, comp_data in components.items():
                total_components += 1
                outputs = comp_data.get("outputs", [])
                total_outputs += len(outputs)

                print(f"  {comp_name}: {len(outputs)} outputs")

                # Check if any output has undefined types
                for i, output in enumerate(outputs):
                    if not isinstance(output, dict):
                        issue = f"{comp_name}: Output {i} is not a dict: {output}"
                        print(f"    ERROR: {issue}")
                        issues_found.append(issue)
                        continue

                    if "types" not in output:
                        issue = f"{comp_name}: Output {i} missing types property"
                        print(f"    ERROR: {issue}")
                        issues_found.append(issue)
                    elif output["types"] is None:
                        issue = f"{comp_name}: Output {i} has null types"
                        print(f"    ERROR: {issue}")
                        issues_found.append(issue)
                    elif not isinstance(output["types"], list):
                        issue = f"{comp_name}: Output {i} types is not a list: {output['types']}"
                        print(f"    ERROR: {issue}")
                        issues_found.append(issue)
                    elif len(output["types"]) == 0:
                        issue = f"{comp_name}: Output {i} has empty types array"
                        print(f"    WARNING: {issue}")
                        issues_found.append(issue)
                    else:
                        print(f"    Output {i} types OK: {output['types']}")

                    # Check for other required fields
                    required_fields = ["name", "display_name"]
                    for field in required_fields:
                        if field not in output:
                            issue = f"{comp_name}: Output {i} missing {field}"
                            print(f"    ERROR: {issue}")
                            issues_found.append(issue)

        print("\n" + "=" * 60)
        print("SUMMARY:")
        print(f"Total components: {total_components}")
        print(f"Total outputs: {total_outputs}")
        print(f"Total issues found: {len(issues_found)}")

        if issues_found:
            print("\nISSUES:")
            for issue in issues_found:
                print(f"  - {issue}")
            return False
        else:
            print("\nAll outputs have valid structure!")
            return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_outputs_structure()
