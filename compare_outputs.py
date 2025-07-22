import json

import requests


def compare_outputs():
    # Get both Langflow and Agno components
    langflow_resp = requests.get("http://localhost:7860/api/v1/all?framework=langflow", timeout=10)
    agno_resp = requests.get("http://localhost:7860/api/v1/all?framework=agno", timeout=10)

    langflow_data = langflow_resp.json()
    agno_data = agno_resp.json()

    print("=== STRUCTURE COMPARISON ===")

    # Get a sample Langflow component output
    langflow_sample = None
    for category, components in langflow_data.items():
        for comp_name, comp_data in components.items():
            outputs = comp_data.get("outputs", [])
            if outputs:
                langflow_sample = outputs[0]
                print(f"Langflow sample output from {comp_name}:")
                for key in sorted(langflow_sample.keys()):
                    print(f"  {key}: {type(langflow_sample[key]).__name__} = {langflow_sample[key]}")
                break
        if langflow_sample:
            break

    print()

    # Get a sample Agno component output
    agno_sample = None
    for category, components in agno_data.items():
        for comp_name, comp_data in components.items():
            outputs = comp_data.get("outputs", [])
            if outputs:
                agno_sample = outputs[0]
                print(f"Agno sample output from {comp_name}:")
                for key in sorted(agno_sample.keys()):
                    print(f"  {key}: {type(agno_sample[key]).__name__} = {agno_sample[key]}")
                break
        if agno_sample:
            break

    print()
    print("=== KEY COMPARISON ===")
    if langflow_sample and agno_sample:
        langflow_keys = set(langflow_sample.keys())
        agno_keys = set(agno_sample.keys())

        print(f"Langflow has {len(langflow_keys)} keys: {sorted(langflow_keys)}")
        print(f"Agno has {len(agno_keys)} keys: {sorted(agno_keys)}")
        print(f"Missing in Agno: {sorted(langflow_keys - agno_keys)}")
        print(f"Extra in Agno: {sorted(agno_keys - langflow_keys)}")
        print(f"Common keys: {sorted(langflow_keys & agno_keys)}")


if __name__ == "__main__":
    compare_outputs()
