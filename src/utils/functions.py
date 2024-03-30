def write_data(a, b, file="data/file_data.txt"):
    with open(file, "w") as out_f:
        print(f"starts: {a}\nkilled tanks: {b}", file=out_f)

def get_data(file="data/file_data.txt"):
    with open(file, "r") as in_f:
        data = [int(x.split(": ")[1]) for x in in_f.readlines() if len(x.strip()) != 0]
    return data