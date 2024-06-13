.data
n: 999
sum: 0
three: 3
five: 5
fifteen: 15
temp: 0
two: 2
three_sum: 0
five_sum: 0
fifteen_sum: 0

.code
; Вычисление three_sum = 3 * (n // 3) * (n // 3 + 1) // 2
LDA n
DIV three
STA temp
INC
MUL temp
STA temp
LDA temp
MUL three
STA temp
LDA temp
DIV two
STA three_sum



; Вычисление five_sum = 5 * (n // 5) * (n // 5 + 1) // 2
LDA n
DIV five
STA temp
INC
MUL temp
STA temp
LDA temp
MUL five
STA temp
LDA temp
DIV two
STA five_sum


; Вычисление fifteen_sum = 15 * (n // 15) * (n // 15 + 1) // 2
LDA n
DIV fifteen
STA temp
INC
MUL temp
STA temp
LDA temp
MUL fifteen
STA temp
LDA temp
DIV two
STA fifteen_sum


; Вычисление result = three_sum + five_sum - fifteen_sum
LDA three_sum
ADD five_sum
STA sum
LDA sum
SUB fifteen_sum
STA sum

; Вывод результата
LDA sum
OUT
HLT
