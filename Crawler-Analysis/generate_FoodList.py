food_list = []
def generate():
    with open('classes.txt','r') as file:
        for line in file:
            food_list.append(line.strip().replace('_',' '))
    return food_list
