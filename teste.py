#create list of randon names
names = ['jose', 'maria', 'joao', 'pedro', 'joana', 'usjos']

#remove names with the letter J
names = [name for name in names if name.lower()[0] != 'j']

print(names)