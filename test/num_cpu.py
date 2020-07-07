import numpy as np
import multiprocessing
import parmap

def square(input_list):
    return [x*x for x in input_list]

if __name__ == '__main__':
    keywordA = ''
    channelA = ''
    startdateA = ''
    enddateA = ''
    nurlA = 0

    keywordB = ''
    channelB = ''
    startdateB = ''
    enddateB = ''
    nurlB = 0

    input_list = [
        [keywordA,channelA,startdateA,enddateA],
        [keywordB,channelB,startdateB,enddateB]
        ]

    num_cores = multiprocessing.cpu_count()
    # 입력 데이터
    data = list(range(1,25)) #[1,2, ..., 24]

    # 입력 데이터를 cpu 수만큼 균등하게 나눠준다. 1차원 배열이 2차원 numpy array 배열이 된다.
    splited_data = np.array_split(data,num_cores)
    #splited_data 는 [np.array([1,2]), np.array([3,4]), ..., np.array([23,24])] 이 된다

    splited_data = [x.tolist() for x in splited_data]
    # splited_data 는 [[1,2],[3,4],[5,6],...,[23,24]] 가 된다.

    #이제 parmap 으로 멀티프로세싱 처리를 하자.
    result = parmap.map(square, splited_data, pm_pbar=True, pm_processes=num_cores)



