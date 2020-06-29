
class DAO:
    def __init__(self,row):
        self.row = row
        self.a_list = []
        self.b_list = []
        print('DAO 객체 생성')
    def add_data(self):
        row = self.row
        periodA = row['periodA']

        periodA = periodA.replace("'", '')
        periodA = periodA.replace("[", '')
        periodA = periodA.replace("]", '')
        periodA = periodA.replace(" ", "")
        periodA = periodA.split(",")
        startdateA = periodA[0]
        enddateA = periodA[1]

        periodB = row['periodB']

        periodB = periodA.replace("'", '')
        periodB = periodA.replace("[", '')
        periodB = periodA.replace("]", '')
        periodB = periodA.replace(" ", "")
        periodB = periodA.split(",")
        startdateB = periodA[0]
        enddateB = periodA[1]

        self.a_list.append(row['keywordA'])
        self.a_list.append(row['channelA'])
        self.a_list.append(row['keywordA'])
        self.a_list.append(row['keywordA'])


