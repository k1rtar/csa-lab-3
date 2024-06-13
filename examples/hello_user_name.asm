.data
prompt_len: 19
prompt: "What is your name?\n"
greeting_len: 8
greeting: "\nHello, "
buffer: RESERVE 30
buffer_pos: 0

.code
    LDA &prompt
    STA buffer_pos
print_prompt:
    LDA (buffer_pos)
    OUT
    LDA buffer_pos
    INC
    STA buffer_pos
    LDA prompt_len
    DEC
    STA prompt_len
    JZ read_name
    JMP print_prompt
read_name:
    LDA &buffer
    STA buffer_pos
read_loop:
    IN
    STA (buffer_pos)
    JZ greet
    OUT
    LDA buffer_pos
    INC
    STA buffer_pos
    JMP read_loop
greet:
    LDA &greeting
    STA buffer_pos
print_greeting:
    LDA (buffer_pos)
    OUT
    LDA buffer_pos
    INC
    STA buffer_pos
    LDA greeting_len
    DEC
    STA greeting_len
    JZ print_name
    JMP print_greeting
print_name:
    LDA &buffer
    STA buffer_pos
print_loop:
    LDA (buffer_pos)
    JZ end
    OUT
    LDA buffer_pos
    INC
    STA buffer_pos
    JMP print_loop
end:
    HLT
