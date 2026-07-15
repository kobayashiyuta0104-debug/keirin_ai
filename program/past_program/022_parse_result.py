import json

with open("result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["tyakujyunItemSubData"]

first = results[0]["syaban"]
second = results[1]["syaban"]
third = results[2]["syaban"]

sanrentan = data["haraiGakuSubData"]["RT3HaraiGakuDispItemSubData"][0]

kumi = sanrentan["kumiBan"]
harai = int(sanrentan["haraiGaku"].replace(",", ""))
ninki = sanrentan["ninki"].replace("(", "").replace(")", "")

if harai < 20000:
    label = "20000未満"
elif harai < 50000:
    label = "20000-49999"
else:
    label = "50000以上"

print("1着:", first)
print("2着:", second)
print("3着:", third)
print("3連単:", kumi)
print("払戻:", harai, "円")
print("人気:", ninki)
print("荒れ分類:", label)