import csv
with open("csv/test.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["名前", "年齢", "職業"])
    writer.writerow(["山田", 30, "会社員"])
    writer.writerow(["佐藤", 25, "エンジニア"])
print("CSV作成完了")