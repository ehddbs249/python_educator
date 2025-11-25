# Python 함수

## 함수 기초

### 함수 정의와 호출
```python
# 기본 함수
def greet():
    print("안녕하세요!")

greet()  # 함수 호출

# 매개변수가 있는 함수
def greet_person(name):
    print(f"안녕하세요, {name}님!")

greet_person("홍길동")

# 반환값이 있는 함수
def add(a, b):
    return a + b

result = add(3, 5)  # 8
```

### 매개변수 종류

#### 위치 인자와 키워드 인자
```python
def introduce(name, age, city):
    print(f"{name}, {age}세, {city} 거주")

# 위치 인자
introduce("홍길동", 25, "서울")

# 키워드 인자
introduce(age=25, name="홍길동", city="서울")

# 혼합 (위치 인자가 먼저)
introduce("홍길동", city="서울", age=25)
```

#### 기본값 매개변수
```python
def greet(name, greeting="안녕하세요"):
    print(f"{greeting}, {name}님!")

greet("홍길동")  # "안녕하세요, 홍길동님!"
greet("홍길동", "반갑습니다")  # "반갑습니다, 홍길동님!"
```

#### 가변 인자 (*args)
```python
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3))      # 6
print(sum_all(1, 2, 3, 4, 5)) # 15
```

#### 키워드 가변 인자 (**kwargs)
```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="홍길동", age=25, city="서울")
```

#### 모든 매개변수 타입 조합
```python
def complex_function(a, b, *args, option=True, **kwargs):
    print(f"a: {a}, b: {b}")
    print(f"args: {args}")
    print(f"option: {option}")
    print(f"kwargs: {kwargs}")

complex_function(1, 2, 3, 4, 5, option=False, name="test")
```

## 고급 함수

### 람다 함수
```python
# 일반 함수
def square(x):
    return x ** 2

# 람다 함수
square_lambda = lambda x: x ** 2

# 활용
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))
sorted_words = sorted(["banana", "apple", "cherry"], key=lambda x: len(x))
```

### 클로저 (Closure)
```python
def outer_function(x):
    def inner_function(y):
        return x + y
    return inner_function

add_5 = outer_function(5)
print(add_5(3))  # 8
```

### 데코레이터
```python
def timer_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    return wrapper

@timer_decorator
def slow_function():
    import time
    time.sleep(1)
    return "완료"

slow_function()
```

### 재귀 함수
```python
# 팩토리얼
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# 피보나치
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## 함수 스코프

### 전역 변수와 지역 변수
```python
global_var = "전역"

def test_scope():
    local_var = "지역"
    print(global_var)  # 접근 가능
    print(local_var)   # 접근 가능

test_scope()
# print(local_var)  # NameError!
```

### global과 nonlocal
```python
count = 0

def increment():
    global count
    count += 1

def outer():
    x = 10
    def inner():
        nonlocal x
        x += 1
    inner()
    print(x)  # 11
```

## 연습 문제

### 입문 레벨
1. 두 수를 받아 더 큰 수를 반환하는 함수를 작성하세요.
2. 리스트의 평균을 계산하는 함수를 작성하세요.

### 중급 레벨
1. 가변 인자를 받아 모든 인자의 곱을 반환하는 함수를 작성하세요.
2. 문자열을 뒤집는 재귀 함수를 작성하세요.

### 고급 레벨
1. 메모이제이션 데코레이터를 구현하세요.
2. 커링(currying)을 구현하는 함수를 작성하세요.
