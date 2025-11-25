# Python 객체지향 프로그래밍 (OOP)

## 클래스와 객체

### 클래스 정의
```python
class Dog:
    # 클래스 변수 (모든 인스턴스가 공유)
    species = "Canis familiaris"

    # 생성자 (초기화 메서드)
    def __init__(self, name, age):
        # 인스턴스 변수
        self.name = name
        self.age = age

    # 인스턴스 메서드
    def bark(self):
        return f"{self.name}가 멍멍!"

    def get_info(self):
        return f"{self.name}, {self.age}살"

# 객체 생성
my_dog = Dog("바둑이", 3)
print(my_dog.bark())      # "바둑이가 멍멍!"
print(my_dog.get_info())  # "바둑이, 3살"
```

### 클래스 메서드와 정적 메서드
```python
class Calculator:
    # 클래스 변수
    count = 0

    def __init__(self):
        Calculator.count += 1

    # 인스턴스 메서드
    def add(self, a, b):
        return a + b

    # 클래스 메서드
    @classmethod
    def get_count(cls):
        return cls.count

    # 정적 메서드
    @staticmethod
    def multiply(a, b):
        return a * b

calc = Calculator()
print(Calculator.get_count())  # 1
print(Calculator.multiply(3, 4))  # 12
```

## 상속 (Inheritance)

### 기본 상속
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{self.name}: 멍멍!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: 야옹!"

dog = Dog("바둑이")
cat = Cat("나비")
print(dog.speak())  # "바둑이: 멍멍!"
print(cat.speak())  # "나비: 야옹!"
```

### super() 사용
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)  # 부모 클래스 초기화
        self.student_id = student_id

    def study(self):
        return f"{self.name}이(가) 공부 중입니다."
```

### 다중 상속
```python
class A:
    def method(self):
        return "A"

class B:
    def method(self):
        return "B"

class C(A, B):  # A가 우선
    pass

c = C()
print(c.method())  # "A" (MRO에 따름)
print(C.__mro__)   # Method Resolution Order 확인
```

## 캡슐화 (Encapsulation)

### 접근 제어
```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner          # public
        self._balance = balance      # protected (관례)
        self.__pin = "1234"          # private (name mangling)

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

    def get_balance(self):
        return self._balance

    def __private_method(self):
        pass

account = BankAccount("홍길동", 10000)
print(account.owner)           # OK
print(account._balance)        # OK (관례상 접근 자제)
# print(account.__pin)         # AttributeError
print(account._BankAccount__pin)  # name mangling으로 접근 가능
```

### 프로퍼티 (Property)
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("반지름은 양수여야 합니다")
        self._radius = value

    @property
    def area(self):
        import math
        return math.pi * self._radius ** 2

circle = Circle(5)
print(circle.radius)  # 5
print(circle.area)    # 78.54...
circle.radius = 10    # setter 호출
```

## 다형성 (Polymorphism)

### 메서드 오버라이딩
```python
class Shape:
    def area(self):
        raise NotImplementedError

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

# 다형성 활용
shapes = [Rectangle(4, 5), Circle(3)]
for shape in shapes:
    print(f"면적: {shape.area()}")
```

## 매직 메서드 (Magic Methods)

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __len__(self):
        return int((self.x**2 + self.y**2)**0.5)

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)   # (4, 6)
print(len(v1))   # 5
```

## 연습 문제

### 입문 레벨
1. 학생 클래스를 만들고 이름, 학번, 성적을 관리하세요.
2. 자동차 클래스를 만들고 주행, 정지 기능을 구현하세요.

### 중급 레벨
1. 은행 계좌 클래스를 만들고 입금, 출금, 이체 기능을 구현하세요.
2. 도형 클래스 계층을 만들고 다형성을 활용하세요.

### 고급 레벨
1. 데코레이터 패턴을 구현하세요.
2. 싱글톤 패턴을 구현하세요.
