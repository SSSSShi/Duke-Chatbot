import requests
import ast

response = requests.get("https://streamer.oit.duke.edu/curriculum/list_of_values/fieldname/SUBJECT?access_token=19d3636f71c152dd13840724a8a48074")

response = ast.literal_eval(response.text)
# Extract values
values = response["scc_lov_resp"]["lovs"]["lov"]["values"]["value"]

# Convert to "CODE - Description" format
lines = [f"{item['code']} - {item['desc']}" for item in values]

# Save to text file
with open("subjects.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

print("Saved to subjects.txt")