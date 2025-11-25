# Python 딕셔너리와 집합

## 딕셔너리 (Dictionary)
키-값 쌍으로 데이터를 저장하는 자료구조입니다.

### 딕셔너리 생성
```python
# 빈 딕셔너리
empty_dict = {}
empty_dict2 = dict()

# 값이 있는 딕셔너리
student = {
    "name": "홍길동",
    "age": 20,
    "major": "컴퓨터공학"
}

# dict() 생성자
person = dict(name="김철수", age=25)
```

### 딕셔너리 접근 및 수정
```python
student = {"name": "홍길동", "age": 20}

# 값 접근
print(student["name"])       # "홍길동"
print(student.get("grade"))  # None (키가 없을 때)
print(student.get("grade", "없음"))  # "없음" (기본값)

# 값 수정
student["age"] = 21

# 새 키-값 추가
student["grade"] = "A"

# 삭제
del student["grade"]
age = student.pop("age")  # 삭제하고 값 반환
```

### 딕셔너리 메서드
```python
student = {"name": "홍길동", "age": 20, "major": "CS"}

# 키, 값, 아이템 조회
keys = student.keys()     # dict_keys(['name', 'age', 'major'])
values = student.values() # dict_values(['홍길동', 20, 'CS'])
items = student.items()   # dict_items([('name', '홍길동'), ...])

# 순회
for key in student:
    print(key, student[key])

for key, value in student.items():
    print(f"{key}: {value}")

# 업데이트
student.update({"age": 21, "gpa": 4.0})

# 모든 항목 삭제
student.clear()
```

### 딕셔너리 컴프리헨션
```python
# 기본 형태
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 조건 포함
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}

# 키-값 뒤집기
original = {"a": 1, "b": 2, "c": 3}
reversed_dict = {v: k for k, v in original.items()}
```

## 집합 (Set)
중복을 허용하지 않고, 순서가 없는 자료구조입니다.

### 집합 생성
```python
# 빈 집합
empty_set = set()  # {}는 빈 딕셔너리!

# 값이 있는 집합
numbers = {1, 2, 3, 4, 5}
unique = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3}
```

### 집합 연산
```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# 합집합
union = a | b  # {1, 2, 3, 4, 5, 6, 7, 8}
union = a.union(b)

# 교집합
intersection = a & b  # {4, 5}
intersection = a.intersection(b)

# 차집합
difference = a - b  # {1, 2, 3}
difference = a.difference(b)

# 대칭차집합 (XOR)
symmetric_diff = a ^ b  # {1, 2, 3, 6, 7, 8}
symmetric_diff = a.symmetric_difference(b)
```

### 집합 메서드
```python
numbers = {1, 2, 3}

# 추가
numbers.add(4)       # {1, 2, 3, 4}
numbers.update([5, 6])  # {1, 2, 3, 4, 5, 6}

# 삭제
numbers.remove(6)    # 없으면 KeyError
numbers.discard(10)  # 없어도 에러 없음
numbers.pop()        # 임의의 요소 삭제

# 부분집합 검사
a = {1, 2}
b = {1, 2, 3, 4}
print(a.issubset(b))    # True
print(b.issuperset(a))  # True
print(a.isdisjoint({5, 6}))  # True (공통 요소 없음)
```

### 집합 활용
```python
# 중복 제거
numbers = [1, 2, 2, 3, 3, 3, 4]
unique_numbers = list(set(numbers))  # [1, 2, 3, 4]

# 멤버십 테스트 (리스트보다 빠름)
valid_users = {"alice", "bob", "charlie"}
if "alice" in valid_users:
    print("유효한 사용자")

# 두 리스트의 공통 요소 찾기
list1 = [1, 2, 3, 4, 5]
list2 = [4, 5, 6, 7, 8]
common = set(list1) & set(list2)  # {4, 5}
```

## 연습 문제

### 입문 레벨
1. 단어의 빈도수를 세는 딕셔너리를 만드세요.
2. 리스트에서 중복을 제거하세요.

### 중급 레벨
1. 두 딕셔너리를 병합하세요.
2. 딕셔너리를 값 기준으로 정렬하세요.

### 고급 레벨
1. 중첩 딕셔너리를 평탄화(flatten)하세요.
2. 집합을 사용하여 그래프의 연결 요소를 찾으세요.
