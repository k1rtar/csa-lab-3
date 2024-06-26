# CSA-LAB-3

- Студент: Таранов Кирилл Викторович
- Преподаватель: Пенской Александр Владимирович.
- `alg -> asm | acc | harv | hw | instr | struct | stream | port | pstr | prob1 | cache`
- Упрощённый вариант.


## Язык программирования

``` ebnf
program ::= { line }

line ::= label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"

label ::= label_name ":"

instr ::= op0
        | op1 label_name

op0 ::= "LDA" address
      | "STA" address
      | "ADD" address
      | "SUB" address
      | "MUL" address
      | "DIV" address
      | "INC"
      | "DEC"
      | "JMP" label_name
      | "JZ" label_name
      | "IN"
      | "OUT"
      | "HLT"

address ::= "&" label_name
          | "(" label_name ")"
          | integer

integer ::= [ "-" ] { <any of "0-9"> }-

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">
```

#### Последовательное выполнение
Выполнение программы происходит последовательно, команда за командой, начиная с первой инструкции в секции `.code` и продолжая до встречи команды `HLT` или другой команды управления потоком, такой как `JMP` или `JZ`.

### Области видимости

#### Глобальные данные
Все данные, объявленные в секции .data, имеют глобальную область видимости. Это означает, что они доступны для всех инструкций в секции .code на протяжении всей программы.

#### Метки
Метки, используемые в секции .code, определяют точки в программе, к которым можно перейти с помощью команд управления потоком. Метки имеют локальную область видимости в пределах программы, но могут быть использованы для переходов из любой точки секции .code.


## Язык программирования Asm

## Организация памяти

Модель памяти процессора:

1. Память команд. Машинное слово -- не определено. Хранит команды программы, реализуется списками словарей. Секция .code 
2. Память данных. Машинное слово -- 32 бит, знаковое. Линейное адресное пространство. Реализуется списком чисел. Используется для хранения данных, объявленных в секции .data.

Адресация:

| name  | code    | desc                     |
|-------|---------|--------------------------|
| addr  | &label  | Загрузка адреса метки    |
| val   | label   | Прямая адресация         |
| indir | (label) | Косвенная адресация      |
| no    | _       | Без операнда             |

Вложенные типы адресации запрещены. Пример: `((label))`, `(&label)`

## Система команд

Особенности процессора:

- Машинное слово -- 32 бит, знаковое.
- Доступ к памяти данных осуществляется по адресу, хранящемуся в специальном регистре `AR`. 
- Поток управления:
    - инкремент `PC` после каждой инструкции;
    - условный (`JZ`) и безусловный (`JMP`) переходы (использование см. в разделе транслятор).

### Набор инструкций

- `LDA` `<address>`	загрузка данных из памяти в аккумулятор, кол-во тактов: 3
- `STA` `<address>`	сохранение данных из аккумулятора в память, кол-во тактов: 3
- `ADD` `<address>`	сложение данных из памяти с аккумулятором, кол-во тактов: 3	
- `SUB` `<address>`	вычитание данных из памяти из аккумулятора, кол-во тактов: 3
- `MUL` `<address>`	умножение данных из памяти на аккумулятор, кол-во тактов: 3	
- `DIV` `<address>`	деление аккумулятора на данные из памяти, кол-во тактов: 3	
- `INC`	увеличение значения аккумулятора на 1, кол-во тактов: 1	
- `DEC`	уменьшение значения аккумулятора на 1, кол-во тактов: 1	
- `JMP` `<label_name>`	безусловный переход, кол-во тактов: 1
- `JZ` `<label_name>` переход, если значение аккумулятора 0, кол-во тактов: 1
- `IN`	ввод данных и сохранение в аккумуляторе, кол-во тактов: 1
- `OUT`	вывод данных из аккумулятора, кол-во тактов: 1
- `HLT`	остановка, кол-во тактов: 1

## Транслятор

Интерфейс командной строки: `translator.py <input_file> <target_file>`

Реализовано в модуле: [translator](./translator.py)

### Принципы работы транслятора

#### Транслятор выполняет следующие этапы:

1. **Чтение и разделение секций `.data` и `.code`**:

- Ассемблерный код разделяется на секции .data и .code. Секция .data содержит данные, а секция .code - команды.

2. **Обработка секции `.data`**:
- каждая строка секции .data обрабатывается для извлечения меток и значений.
- значения могут быть зарезервированы (RESERVE) или представлять собой последовательности символов и чисел.
- значения добавляются в список данных, и соответствующие метки запоминаются с их адресами.
- обработка секции .code:

3. **Каждая строка секции `.code` обрабатывается для извлечения команд и их аргументов.**
- если строка содержит метку, эта метка запоминается с текущим адресом команды.
- команды добавляются в список текстовых инструкций.
- замена меток на адреса и формирование инструкций

4. **В командах текстовой секции метки заменяются на их адреса.**
- форматируются аргументы команд в зависимости от их типа (адрес, значение, косвенный адрес).
5. **Генерация JSON:**
- сформированные данные и текстовые инструкции преобразуются в JSON формат.

### Пример работы

Пример входного ассемблерного кода:
```
.data
hello_len: 13
hello: "Hello, World!"
current_pos: 0

.code
    LDA &hello        
    STA current_pos  
print:
    LDA (current_pos)
    OUT              
    LDA current_pos
    INC               
    STA current_pos 
    LDA hello_len
    DEC
    STA hello_len              
    JZ end           
    JMP print     
end:
    HLT           
```
После обработки этот код преобразуется в следующий JSON:

```
{
    "data": [
        13,
        72,
        101,
        108,
        108,
        111,
        44,
        32,
        87,
        111,
        114,
        108,
        100,
        33,
        0
    ],
    "code": [
        {
            "opcode": "LDA",
            "arg": "&1"
        },
        {
            "opcode": "STA",
            "arg": 14
        },
        {
            "opcode": "LDA",
            "arg": "(14)"
        },
        {
            "opcode": "OUT",
            "arg": null
        },
        {
            "opcode": "LDA",
            "arg": 14
        },
        {
            "opcode": "INC",
            "arg": null
        },
        {
            "opcode": "STA",
            "arg": 14
        },
        {
            "opcode": "LDA",
            "arg": 0
        },
        {
            "opcode": "DEC",
            "arg": null
        },
        {
            "opcode": "STA",
            "arg": 0
        },
        {
            "opcode": "JZ",
            "arg": 12
        },
        {
            "opcode": "JMP",
            "arg": 2
        },
        {
            "opcode": "HLT",
            "arg": null
        }
    ]
}
```

## Модель процессора

Интерфейс командной строки: `machine.py <machine_code_file> <input_file>`

Реализовано в модуле: [machine](./machine.py).

### DataPath

![Data Path](resources/datapath.png)

Реализован в классе `DataPath`.

1. **Регистры**
- AR (Address Register): Содержит адрес для доступа к памяти данных (DataMem).
- DR (Data Register): Содержит данные, которые считываются из памяти или записываются в память.
- ACC (Accumulator): Основной регистр, используемый для арифметических и логических операций.
2. **ALU (Arithmetic Logic Unit)**
- Выполняет арифметические и логические операции на операндах, выбранных MUX-ами, и передает результат обратно в ACC.
3. **DataMem (Data Memory)**
- Память данных, доступ к которой осуществляется через адрес, хранящийся в AR, и управляющие сигналы oe (output enable) и wr (write).
4. **Внешние порты**
- input port: Порт для ввода данных извне.
- output port: Порт для вывода данных вовне.
5. **Флаги**
- Z-флаг: Флаг нуля, который устанавливается, если результат операции в ALU равен нулю.

6. **Управляющие сигналы**

- `latch_addr`: Сигнал для захвата адреса в AR.
- `latch_dr`: Сигнал для захвата данных в DR.
- `latch_acc`: Сигнал для захвата данных в ACC.
- `latch_input`: Сигнал для захвата данных с порта ввода в ACC.
- `latch_output`: Сигнал для вывода данных из ACC в порт вывода.

- `oe` (output enable): Сигнал для чтения данных из памяти.
- `wr` (write): Сигнал для записи данных в память.
- `alu_op`: Управляющий сигнал для выбора операции ALU.
- `sel_addr`: Сигнал выбора для MUX перед AR.
- `sel_op1`: Сигнал выбора для первого операнда ALU.
- `sel_op2`: Сигнал выбора для второго операнда ALU.
- `sel_acc`: Сигнал выбора для MUX перед ACC.

### ControlUnit

![Control Unit](resources/controlunit.png)

Реализован в классе `ControlUnit`.

- Hardwired (реализовано полностью на Python).
- Метод `execute_instruction` моделирует выполнение полного цикла инструкции (1-3 такта процессора).
- `current_phase` необходим для многотактовых инструкций;
- Цикл симуляции осуществляется в функции step.
- Шаг моделирования соответствует одной инструкции с выводом состояния в журнал.
- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования лимитировано.
- Остановка моделирования осуществляется при:
    - исключении StopIteration -- если выполнена инструкция HLT.


### Тестирование

Golden tests реализованны в файле [тестов](golden_asm_test.py), данные для проверки хранятся [здесь](golden).

### Линтер

Линтер используется для проверки стиля кода и поиска потенциальных ошибок. В этом проекте используется `Ruff` для линтинга Python-кода.

#### Настройка линтера

Конфигурация для линтера `Ruff` находится в файле [pyproject](pyproject.toml).

## Статистика
<div style="overflow-x: auto;">

| ФИО                             | алг   | LoC | code байт | code инстр. | инстр. | такт. | вариант |
|---------------------------------|-------|-----|-----------|-------------|--------|-------|---------|
|Таранов Кирилл Викторович        | hello | 21  |  -        |      13      |   131   | 513   | asm \| acc \| harv \| hw \| instr \| struct \| stream \| port \| pstr \| prob1 \| - |
|Таранов Кирилл Викторович        | cat   | 8   |  -        |      5      |   26   | 78    | asm \| acc \| harv \| hw \| instr \| struct \| stream \| port \| pstr \| prob1 \| - |
|Таранов Кирилл Викторович        | hello_user_name | 61 | -|      44     |   371  | 1439   | asm \| acc \| harv \| hw \| instr \| struct \| stream \| port \| pstr \| prob1 \| - |
|Таранов Кирилл Викторович        | prob1 | 71  |  -        |      44     |   44 | 99 | asm \| acc \| harv \| hw \| instr \| struct \| stream \| port \| pstr \| prob1 \| - |
</div>


