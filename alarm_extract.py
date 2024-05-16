# %%
import xmltodict
import os
import pandas as pd


def xml_to_dict(xml_string):
    # Convert XML to dictionary
    xml_dict = xmltodict.parse(xml_string)
    return xml_dict


def read_file_as_string(file_path):
    try:
        with open(file_path, "r") as file:
            # Read the entire file into a string
            file_contents = file.read()
            # Remove line breaks (replace them with an empty string)
            file_contents = file_contents.replace("\n", "").replace("\r", "")

            return file_contents
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def wrapped_in_schema(empirbus_dict: dict):
    return "components" not in empirbus_dict["project"]


def unwrap(boat_name, result_dict, lista_larm: list):
    for j in range(len(result_dict)):
        comp_id = result_dict[j]["@componentId"]
        if comp_id == "1292":
            larm_skit = result_dict[j]
            larm_id = larm_skit["@id"] if "@id" in larm_skit else ""
            for larm in larm_skit["properties"]["property"]:
                if larm["@id"] == "31":
                    larm_text = larm["@value"]
                if larm["@id"] == "15":
                    larm_severity = larm["@value"]
                if larm["@id"] == "4":
                    actual_larm_id = larm["@value"]
            if larm_text != "":
                lista_larm.append(
                    {
                        "boat": boat_name,
                        "id": larm_id,
                        "text": larm_text,
                        "larm_severity": larm_severity,
                        "actual_id": actual_larm_id,
                    }
                )


# %%

folder_path = "input/"  # Replace with the path to your folder

# Get a list of all files in the folder
file_names = [
    f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
]
lista_larm = []
old_length = 0
for _, file_name in enumerate(file_names):
    boat_name = file_name.replace(" ", "_").split("SSRS_")[1].split("_")[0]
    file_string = read_file_as_string(f"{folder_path}/{file_name}")
    xml_string = file_string
    result_dict = xml_to_dict(xml_string)
    if wrapped_in_schema(result_dict):
        if isinstance(result_dict["project"]["schemas"]["schema"], list):
            for i in range(len(result_dict["project"]["schemas"]["schema"])):
                if (
                    "components" in result_dict["project"]["schemas"]["schema"][i]
                    and result_dict["project"]["schemas"]["schema"][i]["components"]
                    is not None
                    and "component"
                    in result_dict["project"]["schemas"]["schema"][i]["components"]
                ):
                    unwrap(
                        boat_name=boat_name,
                        result_dict=result_dict["project"]["schemas"]["schema"][i][
                            "components"
                        ]["component"],
                        lista_larm=lista_larm,
                    )
        if isinstance(result_dict["project"]["schemas"]["schema"], dict):
            if (
                "components" in result_dict["project"]["schemas"]["schema"]
                and result_dict["project"]["schemas"]["schema"]["components"]
                is not None
                and "component"
                in result_dict["project"]["schemas"]["schema"]["components"]
            ):
                unwrap(
                    boat_name=boat_name,
                    result_dict=result_dict["project"]["schemas"]["schema"][
                        "components"
                    ]["component"],
                    lista_larm=lista_larm,
                )
    else:
        unwrap(
            boat_name=boat_name,
            result_dict=result_dict["project"]["components"]["component"],
            lista_larm=lista_larm,
        )
    new_length = len(lista_larm)
    if new_length == old_length:
        print(boat_name)
    old_length = new_length

# %%
larm_frame = pd.DataFrame(lista_larm)

# %%
larm_frame.to_excel("larm.xlsx")

# %%
