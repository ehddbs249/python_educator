# Python 리스트와 튜플

## 리스트 (List)
순서가 있고, 변경 가능한(mutable) 자료구조입니다.

### 리스트 생성
```python
# 빈 리스트
empty_list = []
empty_list2 = list()

# 값이 있는 리스트
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
nested = [[1, 2], [3, 4], [5, 6]]
```

### 리스트 인덱싱
```python
fruits = ["사과", "바나나", "오렌지", "포도"]

print(fruits[0])   # "사과"
print(fruits[-1])  # "포도"
print(fruits[1:3]) # ["바나나", "오렌지"]
```

### 리스트 메서드
```python
numbers = [1, 2, 3]

# 추가
numbers.append(4)        # [1, 2, 3, 4]
numbers.insert(0, 0)     # [0, 1, 2, 3, 4]
numbers.extend([5, 6])   # [0, 1, 2, 3, 4, 5, 6]

# 삭제
numbers.remove(0)        # 값으로 삭제
popped = numbers.pop()   # 마지막 요소 삭제 및 반환
del numbers[0]           # 인덱스로 삭제

# 검색
index = numbers.index(3) # 값의 인덱스
count = numbers.count(3) # 값의 개수

# 정렬
numbers.sort()           # 오름차순 정렬
numbers.sort(reverse=True)  # 내림차순 정렬
numbers.reverse()        # 역순으로 변경

# 복사
copied = numbers.copy()  # 얕은 복사
```

### 리스트 연산
```python
a = [1, 2, 3]
b = [4, 5, 6]

# 연결
c = a + b  # [1, 2, 3, 4, 5, 6]

# 반복
d = a * 2  # [1, 2, 3, 1, 2, 3]

# 멤버십 테스트
print(2 in a)  # True

# 길이
print(len(a))  # 3
```

## 튜플 (Tuple)
순서가 있고, 변경 불가능한(immutable) 자료구조입니다.

### 튜플 생성
```python
# 빈 튜플
empty_tuple = ()
empty_tuple2 = tuple()

# 값이 있는 튜플
point = (3, 4)
single = (1,)  # 요소가 하나일 때 콤마 필수
mixed = (1, "hello", 3.14)
```

### 튜플 활용
```python
# 패킹과 언패킹
coordinates = (10, 20, 30)
x, y, z = coordinates

# 값 교환
a, b = 1, 2
a, b = b, a  # a=2, b=1

# 함수에서 여러 값 반환
def get_min_max(numbers):
    return min(numbers), max(numbers)

min_val, max_val = get_min_max([1, 2, 3, 4, 5])
```

### 리스트 vs 튜플
| 특성 | 리스트 | 튜플 |
|------|--------|------|
| 변경 가능 | O | X |
| 속도 | 느림 | 빠름 |
| 메모리 | 더 많이 사용 | 적게 사용 |
| 사용 시점 | 데이터 변경 필요 | 데이터 보호 필요 |

```python
# 튜플을 딕셔너리 키로 사용 가능
locations = {
    (0, 0): "원점",
    (1, 0): "동쪽",
}

# 리스트는 불가능 (unhashable type)
# locations = {[0, 0]: "원점"}  # TypeError!
```

## 연습 문제

### 입문 레벨
1. 5개의 정수를 입력받아 리스트에 저장하고 합계와 평균을 구하세요.
2. 리스트에서 최댓값과 최솟값을 찾으세요.

### 중급 레벨
1. 두 리스트의 교집합, 합집합, 차집합을 구하세요.
2. 2차원 리스트(행렬)의 행과 열을 교환하세요.

### 고급 레벨
1. 리스트를 사용하여 스택(LIFO)과 큐(FIFO)를 구현하세요.
2. 정렬 알고리즘(버블, 선택, 삽입)을 직접 구현하세요.
