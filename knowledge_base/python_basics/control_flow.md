# Python 제어문

## 조건문 (Conditional Statements)

### if 문
```python
age = 20

if age >= 18:
    print("성인입니다")
```

### if-else 문
```python
score = 75

if score >= 60:
    print("합격")
else:
    print("불합격")
```

### if-elif-else 문
```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"학점: {grade}")
```

### 중첩 조건문
```python
age = 25
has_license = True

if age >= 18:
    if has_license:
        print("운전 가능")
    else:
        print("면허 필요")
else:
    print("미성년자")
```

### 조건 표현식 (삼항 연산자)
```python
age = 20
status = "성인" if age >= 18 else "미성년자"
```

## 반복문 (Loops)

### for 문
```python
# 리스트 순회
fruits = ["사과", "바나나", "오렌지"]
for fruit in fruits:
    print(fruit)

# range() 사용
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

for i in range(1, 6):
    print(i)  # 1, 2, 3, 4, 5

for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# enumerate() 사용
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

### while 문
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### break와 continue
```python
# break: 반복문 종료
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: 다음 반복으로 건너뛰기
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9
```

### else와 함께 사용
```python
# 반복문이 정상 종료되면 else 실행
for i in range(5):
    print(i)
else:
    print("반복 완료")

# break로 종료되면 else 실행 안 됨
for i in range(5):
    if i == 3:
        break
    print(i)
else:
    print("이 메시지는 출력되지 않음")
```

## 중첩 반복문
```python
# 구구단
for i in range(2, 10):
    for j in range(1, 10):
        print(f"{i} x {j} = {i*j}")
    print()
```

## 리스트 컴프리헨션
```python
# 기본 형태
squares = [x**2 for x in range(10)]

# 조건 포함
evens = [x for x in range(20) if x % 2 == 0]

# 중첩
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
```

## 연습 문제

### 입문 레벨
1. 1부터 10까지 숫자 중 짝수만 출력하세요.
2. 입력받은 숫자가 양수, 음수, 0인지 판별하세요.

### 중급 레벨
1. 구구단 2단부터 9단까지 출력하세요.
2. 피보나치 수열의 처음 20개 항을 출력하세요.

### 고급 레벨
1. 소수를 찾는 프로그램을 작성하세요.
2. 리스트 컴프리헨션으로 행렬 전치를 구현하세요.
