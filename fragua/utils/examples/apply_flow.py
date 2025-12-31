"""Example how to apply entire flow."""

# pylint: disable=duplicate-code
# mypy: ignore-errors

from pathlib import Path
import fragua as fg

# --- Config ---
BASE_DIR = Path(__file__).parent
INPUT_XLSX = BASE_DIR / "test_files" / "input_files" / "test_data.xlsx"
OUTPUT_XLSX = BASE_DIR / "test_files" / "output_files"

# create environment
env_1 = fg.FraguaEnvironment(env_name="fragua_1", fg_config=True)

# create an agent
env_1.create(fg.AGENT, "agent_1")

# get the agent from agent set
agent = env_1.get(fg.AGENT, "agent_1")

# here you can do a few different things;

# 1- use 'work' function by passing the required params like the following.
# I recommend do this when you previously added new functions and you want to use them.
agent.work(target_type=fg.EXCEL, action=fg.EXTRACT, path=str(INPUT_XLSX))

agent.work(
    target_type=fg.REPORT,
    action=fg.TRANSFORM,
    apply_to="extracted_data",
    save_as="transformed_data",
)
agent.work(
    target_type=fg.EXCEL,
    action=fg.LOAD,
    apply_to=["extracted_data", "transformed_data"],
    directory=str(OUTPUT_XLSX),
    file_name="output_file",
)

# 2- if you not need to use custom functions, you can use this options;

# also here you have 'from_csv', 'from_sql' and 'from_api' and the following.
agent.from_excel(save_as="extracted_data", path=str(INPUT_XLSX))

# also here you have 'to_analysis', 'to_ml' and the following.
agent.to_report(apply_to="extracted_data", save_as="transformed_data")

# and here you have 'to_csv', 'to_api','to_sql' and the following.
agent.to_excel(
    apply_to=["extracted_data", "transformed_data"],
    directory=str(OUTPUT_XLSX),
    file_name="output_file",
)

# 3 for an third option you can do an chaining line of functions using all the options.
# like this;
agent.from_excel(save_as="extracted_data", path=str(INPUT_XLSX)).work(
    function="transform_pipeline_func",
    apply_to="extracted_data",
    save_as="transformed_data",
).to_excel(
    apply_to=["extracted_data", "transformed_data"],
    directory=str(OUTPUT_XLSX),
    file_name="output_file",
)
