# Python 변수와 자료형

## 변수 (Variables)
변수는 데이터를 저장하는 공간입니다. Python에서는 변수를 선언할 때 자료형을 명시하지 않아도 됩니다.

### 변수 선언
```python
name = "홍길동"  # 문자열
age = 25        # 정수
height = 175.5  # 실수
is_student = True  # 불리언
```

### 변수 명명 규칙
- 문자, 숫자, 밑줄(_)만 사용 가능
- 숫자로 시작할 수 없음
- 대소문자 구분
- 예약어 사용 불가 (if, for, while 등)

## 기본 자료형

### 1. 숫자형 (Numbers)
```python
# 정수 (int)
x = 10
y = -5

# 실수 (float)
pi = 3.14159
temperature = -10.5

# 복소수 (complex)
z = 3 + 4j
```

### 2. 문자열 (String)
```python
# 문자열 생성
name = "Python"
greeting = 'Hello, World!'
multiline = """여러 줄
문자열"""

# 문자열 연산
full_name = "Hong" + " " + "Gildong"  # 연결
repeated = "Ha" * 3  # 반복: "HaHaHa"

# 문자열 인덱싱과 슬라이싱
s = "Python"
print(s[0])    # 'P'
print(s[-1])   # 'n'
print(s[0:3])  # 'Pyt'
```

### 3. 불리언 (Boolean)
```python
is_active = True
is_empty = False

# 비교 연산 결과
result = 10 > 5  # True
```

### 4. None
```python
# 값이 없음을 나타냄
result = None
```

## 형 변환 (Type Conversion)
```python
# 문자열 → 정수
num_str = "123"
num = int(num_str)  # 123

# 정수 → 문자열
age = 25
age_str = str(age)  # "25"

# 문자열 → 실수
price_str = "19.99"
price = float(price_str)  # 19.99

# 자료형 확인
print(type(123))      # <class 'int'>
print(type("hello"))  # <class 'str'>
```

## 연습 문제

### 입문 레벨
1. 자신의 이름, 나이, 키를 변수에 저장하고 출력하세요.
2. 두 숫자의 합, 차, 곱, 나눗셈 결과를 출력하세요.

### 중급 레벨
1. 사용자로부터 입력받은 문자열을 정수로 변환하여 계산하세요.
2. f-string을 사용하여 변수들을 포맷팅하세요.

### 고급 레벨
1. isinstance()를 사용하여 자료형을 검사하는 함수를 만드세요.
2. 다양한 자료형 간의 형 변환 예외 처리를 구현하세요.
