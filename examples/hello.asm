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
