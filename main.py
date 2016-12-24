import csv


with open('swiss-pois.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='"', dialect='excel')
	print (type(spamreader))
	for row in spamreader: {
		#print(', '.join(row))
	}
	