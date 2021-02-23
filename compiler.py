#ELENI MOUZAKI AM:3280 USERNAME:cse63280
#PANAGIOTIS PAPAIOANNOU AM:3309 USERNAME:cse63309

#written and compiled using Python 2.7.16

#to run type python compiler.py
#and then when prompted type the filename with the .min extension

import sys

keyWordsSet={'program','declare','if','then','else','while','doublewhile','loop',
               'exit','forcase','incase','when','default','not','and','or','function',
               'procedure','call','return','in','inout','input','print'}

symbolSet={'+','-','*','=',';',',','(',')','[',']','{','}'}

IDs=[]
functionIDs=[]
varIDs=[[]]



#Lexical analyser
#if everything is okay returns the word that was just read
#else quits the program with an ERROR
def lex():
    global line                         #line counter for the errors
    state=0
    word=''
    while state != -1:
        char=f.read(1)                  #reads next character
        if(state==0):
            if(char.isspace()):
                if(char=='\n'):
                    line+=1
                state=0
            elif(char.isalpha()):
                word+=char
                state=1
            elif(char.isdigit()):
                word+=char
                state=2
            elif(char in symbolSet):
                word+=char
                state=-1
            elif(char=='<'):
                word+=char
                state=3
            elif(char=='>'):
                word+=char
                state=4
            elif(char==':'):
                word+=char
                state=5
            elif(char=='/'):
                state=6
            else:
                print("ERROR:Uknown Character: '"+char+"' in line "+str(line))
                quit()
        elif state==1:
            #while state is 1 construct the word
            if(char.isalpha() or char.isdigit()):
                word+=char
            elif(char.isspace()):
                if(char=='\n'):
                    line+=1
                if(word not in keyWordsSet and word not in IDs):
                    IDs.append(word)
                state=-1
            else:
                if(word not in keyWordsSet and word not in IDs):
                    IDs.append(word)
                f.seek(f.tell()-1)#go back one character because a new word is starting
                state=-1
        elif state==2:
            #while state is 2 construct the number but check if is out of bounds
            if(char.isdigit()):
                word+=char
            elif(char.isalpha()):
                print("ERROR:Letter after digit in line "+str(line))
                quit()
            elif(char.isspace()):
                if(char=='\n'):
                    line+=1
                value=int(word)
                if(value>32767 or value<-32767):
                    print("ERROR:Number out of range in line "+str(line))
                    quit()
                state=-1
            else:
                value=int(word)
                if(value>32767 or value<-32767):
                    print("ERROR:Number out of range in line "+str(line))
                    quit()
                f.seek(f.tell()-1)
                state=-1
        elif state==3:
            if(char=='=' or char=='>'):
                word+=char
                state=-1
            elif(char.isspace()):
                if(char=='\n'):
                    line+=1
                state=-1
            else:
                f.seek(f.tell()-1)
                state=-1
        elif state==4:
            if(char=='='):
                word+=char
                state=-1
            elif(char.isspace()):
                if(char=='\n'):
                    line+=1
                state=-1
            else:
                f.seek(f.tell()-1)
                state=-1
        elif state==5:
            if(char=='='):
                word+=char
                state=-1
            elif(char.isspace()):
                if(char=='\n'):
                    line+=1
                state=-1
            else:
                f.seek(f.tell()-1)
                state=-1
        elif state==6:
            #'/*' comment
            if(char=='*'):
                #ingore all the following character until the comment closes
                #if a second comment starts error
                while char:
                    char=f.read(1)
                    if(char=='/'):
                        char=f.read(1)
                        if(char=='\n'):
                            line+=1
                        elif(char=='*' or char=='/'):
                            print("ERROR:Cannot open new comment inside a comment in line "+str(line))
                            quit()
                    elif(char=='*'):
                        char=f.read(1)
                        if(char=='\n'):
                            line+=1
                        elif(char=='/'):
                            state=0
                            break
                    elif(char=='\n'):
                        line+=1
                if(state==6):
                    print("ERROR:Comments need to close in line "+str(line))
                    quit()
            #'//' comment
            elif(char=='/'):
                while char:
                    #ingore all the following character until the comment closes
                    #if a second comment starts error
                    char=f.read(1)
                    if(char=='/'):
                        char=f.read(1)
                        if(char=='\n'):
                            line+=1
                            state=0
                            break
                        elif(char=='*' or char=='/'):
                            print("ERROR:Cannot open new comment inside a comment in line "+str(line))
                            quit()
                    elif(char=='\n'):
                        line+=1
                        state=0
                        break
            elif(char.isspace()):
                if(char=='\n'):
                    line+=1
                word+='/'
                state=-1
            else:
                state=0
    return word

#Here starts the syntactical analysis
#first checks if "program ID {" is written
#after that checks the rest of the program
#with block() which contains the basic structure of a MINIMAL++ code
#the declarations, the functions or procedures and the statements
def program():
    global token
    global program_name
    if(token=="program"):
        token=lex()
        if(token in IDs):
            IDs.remove(token) #Main program ID removed from IDs list so that other functions-procedures can't have the same name
            program_name=token #important for halt
            token=lex()
            if(token=='{'):
                token=lex()
                addNewScope()
                block(program_name)
                if(token!='}'):
                    print("ERROR:Missing '}' in line "+str(line))
                    print("Main program should hava both '{' and '}'")
                    quit()
            else:
                print("ERROR:Missing '{' in line "+str(line))
                print("Main Program should hava both '{' and '}'")
                quit()
        else:
            print("ERROR:Needs a legitimate Main Program ID in line "+str(line))
            quit()
    else:
        print("ERROR:'Program' keyword missing in line "+str(line))
        quit()

def block(block_name):
    declarations()
    subprograms()
    genquad("begin_block", block_name, "_", "_")
    if(block_name!=program_name):#program_name isn't inside the scopes so it cant be searched
        (entity,entity_level)=searchFuncEntity(block_name)
        entity.insert(2,nextquad()) #this is the start_quad of this block
        if(entity[1]=='func'):
            returned.append([block_name,0]) #makes sure that a function always returns
    statements()
    if(block_name==program_name):
        genquad("halt", "_", "_", "_") #if main program ID then halt
    genquad("end_block", block_name, "_","_")
    varIDs.pop() #allowing to declare the same varibles in the same nested level
    if(block_name!=program_name):#update func framelength now that it ended
        framelength=scopes[-1][0][1]
        entity.append(framelength)
    fillFinalCodeList(block_name)
    if(len(returned)>0 and block_name!=program_name):#check if the current function returned something
        if(returned[0][1]==0):
            print("ERROR:Function "+ block_name +" does not return")
            quit()
        else:
            returned.pop()
    deleteScope()

def declarations():
    global token
    if(token=="declare"):
        token=lex()
        varlist()
        if(token==';'):
            token=lex()
            declarations()
        else:
            print("ERROR:Missing ';' after 'declare' in line "+str(line))
            quit()

def varlist():
    global token
    if(token in IDs):
        if(token in varIDs[nested_level-1]):
            print("ERROR:Duplicate declared variables on same level in line "+str(line))
            quit()
        varIDs[nested_level-1].append(token)
        addNewVarEntity(token)
        token=lex()
        if(token in IDs):
            print("ERROR:Declared variables should be separated by ',' in line "+str(line))
            quit()
        while(token==','):
            token=lex()
            if(token in IDs):
                if(token in varIDs[nested_level-1]):
                    print("ERROR:Duplicate declared variables on same level in line "+str(line))
                    quit()
                varIDs[nested_level-1].append(token)
                addNewVarEntity(token)
                token=lex()
            else:
                print("ERROR:Needs a legitimate variable ID in line "+str(line))
                quit()

def subprograms():
    global token
    global func_flag
    if(token=="function" or token=="procedure"):
        if(token=="procedure"):#flag for the Symbol Talbe
            func_flag=1
        else:
            func_flag=0
        token=lex()
        if(token in IDs and token!=program_name and token not in functionIDs):
            functionIDs.append(token)#not allowing same name functions or procedures
            IDs.remove(token)#removed from IDs list so that variables can have the same name of a function
            func_name=token
            token=lex()
            addNewScope()
            varIDs.append([])#new function so new variables can be declared
            addNewFuncEntity(func_name)
            funcbody(func_name)
            subprograms()
        else:
            print("ERROR:Needs a legitimate subprogram ID in line "+str(line))
            quit()

def funcbody(func_name):
    global token
    formalpars(func_name)
    if(token=='{'):
        token=lex()
        block(func_name)
        if(token!='}'):
            print("ERROR:Missing '}' in line "+str(line))
            print("Subprograms should have both '{' and '}'")
            quit()
        token=lex()
    else:
        print("ERROR:Missing '{' in line "+str(line))
        print("Subprograms should have both '{' and '}'")
        quit()

def formalpars(func_name):
    global token
    if(token=='('):
        token=lex()
        formalparlist(func_name)
        if(token!=')'):
            print("ERROR:Missing ')' in line "+str(line))
            print("Subprogram parameters should be inside both '(' and ')'")
            quit()
        token=lex()
    else:
        print("ERROR:Missing '(' in line "+str(line))
        print("Subprogram parameters should be inside both '(' and ')'")
        quit()

def formalparlist(func_name):
    formalparitem(func_name)

def formalparitem(func_name):
    global token
    if(token=='in' or token=='inout'):
        par_mode=token
        token=lex()
        if(token in IDs):
            addNewArgument(func_name,par_mode)
            addNewParEntity(token,par_mode)
            token=lex()
            if(token==','):
                token=lex()
                formalparitem(func_name)
            elif(token in IDs):
                print("ERROR:Subprogram parameters should be separated by ',' in line "+str(line))
                quit()
        else:
            print("ERROR:Needs a legitimate parameter ID in line "+str(line))
            quit()

def statements():
    global token
    if(token=='{'):
        token=lex()
        statement()
        while(token==';'):
            token=lex()
            statement()
        if(token!='}'):
            print("ERROR:Multiple statements should be inside '{' and '}' in line "+str(line))
            quit()
        token=lex()
    else:
        statement()
        if(token==';'):
            print("ERROR:Single statements cannot end with ';' in line "+str(line))
            quit()

def statement():
    global token
    if(token in IDs):
        z=token
        token=lex()
        x=assignment_stat()
        genquad(":=",x, "_", z)
    elif(token=="if"):
        token=lex()
        if_stat()
    elif(token=="while"):
        token=lex()
        while_stat()
    elif(token=="doublewhile"): #not implemented for intermidate and final code
        token=lex()
        doublewhile_stat()
    elif(token=="loop"): #not implemented for intermidate and final code
        token=lex()
        loop_stat()
    elif(token=="exit"): #not implemented for intermidate and final code
        token=lex()
        exit_stat()
    elif(token=="forcase"):
        token=lex()
        forcase_stat()
    elif(token=="incase"): #not implemented for intermidate and final code
        token=lex()
        incase_stat()
    elif(token=="call"):
        token=lex()
        call_stat()
    elif(token=="return"):
        token=lex()
        return_stat()
    elif(token=="input"):
        token=lex()
        input_stat()
    elif(token=="print"):
        token=lex()
        print_stat()

def assignment_stat():
    global token
    if(token==':='):
        token=lex()
        res=expression()
    else:
        print("ERROR:Missing assignment operator: ':=' in line "+str(line))
        quit()
    return res

def expression():
    global token
    op_temp=optional_sign() #optional_sign() returns only if there is + or - and generates a corresponding quad
    x=term()
    if(op_temp!=None):
        w1=newTemp()
        genquad(op_temp,0,x,w1)
        x=w1
    while(token=='+' or token=='-'):
        op=token
        token=lex()
        y=term()
        w2=newTemp()
        genquad(op,x,y,w2)
        x=w2
    return x    

def optional_sign():
    global token
    if(token=='+' or token=='-'):
        op=token
        token=lex()
        return op

def term():
    global token
    x=factor()
    while(token=='*' or token=='/'):
        op=token
        token=lex()
        y=factor()
        w=newTemp()
        genquad(op,x,y,w)
        x=w
    return x

def factor():
    global token
    global pars
    global depth
    if(token=='('):
        token=lex()
        x=expression()
        if(token!=')'):
            print("ERROR:Missing ')' in line "+str(line))
            quit()
        token=lex()
        return x
    elif(token in IDs):
        id=token
        token=lex()
        if(idtail()==False):
            return id
        else:
            #idtail returned True
            #so now we must check if the correct arguments have been given
            try:
                (func_entity,entity_level)=searchFuncEntity(id)
                func_type=func_entity[1]
                arguments=func_entity[3]
            except:
                print("ERROR:Undeclared function in line "+str(line))
                quit()
            if(func_type!='func'):
                print("ERROR:Procedures can only be used with the 'call' statement in line "+str(line))
                quit()
            pars_length=len(pars)
            arguments_length=len(arguments)
            if(depth>=2):#this is useful for multiple function calls
                         #i.e. res:=max(in max(in x, in y), in max(in k, in l)))
                temp_pars_length=0
                for i in range(len(pars)):
                    if(depth==pars[i][0]):
                        temp_pars_length+=1
                pars_length=temp_pars_length 
            if(pars_length!=arguments_length):
                print("ERROR:Function arguments must match in line "+str(line))
                quit()
            for i in range(len(arguments)):
                if(pars[i][2]=='CV'):
                    arg='in'
                elif(pars[i][2]=='REF'):
                    arg='inout'
                if(arg!=arguments[i]):
                    print("ERROR:Function arguments must match in line "+str(line))
                    print("Found '"+arg+"' but '"+arguments[i]+"' was expected for function '"+id+"'") 
                    quit()
            w=newTemp()
            remaining_pars=[]
            for parameter in pars :#this is useful for multiple function calls
                                   #i.e. res:=max(in max(in x, in y), in max(in k, in l)))
                if(parameter[0]==depth):#only the currently called quads must be added
                    genquad("par",parameter[1],parameter[2],"_")
                else:
                    remaining_pars.append(parameter)
            pars=remaining_pars
            depth-=1
            genquad("par",w,"RET","_")
            genquad("call","_","_",id)
            return w
    elif(token.isdigit()):
        x=token
        token=lex()
        return x
    else:
        print("ERROR:'(' or ID or number expected in line "+str(line))
        quit()  
          
def idtail():
    global token
    if(token=='('):
        actualpars()
        return True      
    else:
        return False

def actualpars():
    global token
    global depth
    if(token=='('):
        token=lex()
        depth+=1
        actualparlist()
        if(token!=')'):
            print("ERROR:Missing ')' in line "+str(line))
            print("Fucntion or Procedure parameters should be inside '(' and ')'")
            quit()
        token=lex()
    
def actualparlist():
    global token
    if(token=="in" or token=="inout"):
        actualparitem()
        while(token==','):
            token=lex()
            actualparitem()

def actualparitem():
    global token
    if(token=="in"):
        token=lex()
        expres=expression()
        pars.append([depth,expres,"CV"])
    elif(token=="inout"):
        token=lex()
        if(token not in IDs):
            print("ERROR:Needs a legitimate inout ID in line "+str(line))
            quit()
        id=token
        pars.append([depth,id,"REF"])
        token=lex()
    else:
        print("ERROR:Missing 'in' or 'inout' "+str(line))
        quit()

def if_stat():
    global line
    global token
    if(token=='('):
        token=lex()
        (b_true,b_false)=condition()
        if(token==')'):
            token=lex()
            if(token=="then"):
                token=lex()
                backpatch(b_true,nextquad())
                statements()
                if_list=makeList(nextquad())
                genquad("jump","_","_","_")
                backpatch(b_false,nextquad())
                elsepart()
                backpatch(if_list,nextquad())
            else:
                print("ERROR:Missing 'then' in line "+str(line))
        else:
            print("ERROR:Missing ')' in line "+str(line))
            print("If conditions should be inside '(' and ')'")
            quit()
    else:
        print("ERROR:Missing '(' in line "+str(line))
        print("If condition should be inside '(' and ')'")
        quit()

def condition():
    global token
    (b_true,b_false)=boolterm()
    while(token=="or"):
        backpatch(b_false,nextquad())
        token=lex()
        (q2_true,q2_false)=boolterm()
        b_true=mergeList(b_true, q2_true)
        b_false=q2_false
    return [b_true,b_false]

def boolterm():
    global token
    (q_true,q_false)=boolfactor()
    while(token=="and"):
        backpatch(q_true,nextquad())
        token=lex()
        (r2_true,r2_false)=boolfactor()
        q_false=mergeList(q_false,r2_false)
        q_true=r2_true
    return (q_true,q_false)

def boolfactor():
    global line
    global token
    if(token=="not"):
        token=lex()
        if(token=='['):
            token=lex()
            lists=condition()
            lists.reverse() #swap true and false list because of the "not" operator
            if(token!=']'):
                print("ERROR:Missing ']' in line "+str(line))
                print("Boolean operations should be inside '[' and ']'")
                quit()
            token=lex()
        else:
            print("ERROR:Missing '[' in line "+str(line))
            print("Boolean operations should be inside '[' and ']'")
            quit()
    elif(token=='['):
        token=lex()
        lists=condition()
        if(token!=']'):
            print("ERROR:Missing ']' in line "+str(line))
            quit()
        token=lex()
    else:
        x=token
        expres1=expression()
        relop=relational_oper()
        y=token
        expres2=expression()
        true_list=makeList(nextquad())
        genquad(relop,expres1,expres2,"_")
        false_list=makeList(nextquad())
        genquad("jump","_","_","_")
        lists=(true_list,false_list)
    return lists

def relational_oper():
    global line
    global token
    if(token!='=' and token!='<=' and token!='>='and token!='>' and token!='<' and token!='<>'):
        print("ERROR:Missing relational operator in line "+str(line))
        quit()
    else:
        relop=token
        token=lex()
        return relop

def elsepart():
    global token
    if(token=="else"):
        token=lex()
        statements()

def while_stat():
    global line
    global token
    bquad=nextquad()
    if(token=='('):
        token=lex()
        (b_true,b_false)=condition()
        if(token!=')'):
            print("ERROR:Missing ')' in line "+str(line))
            print("While conditions should be inside '(' and ')'")
            quit()
        token=lex()
    else:
        print("ERROR:Missing '(' in line "+str(line))
        print("While conditions should be inside '(' and ')'")
        quit()
    backpatch(b_true, nextquad())
    statements()
    genquad("jump","_","_",bquad)
    backpatch(b_false,nextquad())

def doublewhile_stat():#not implemented for intermidate and final code
    global line
    global token
    if(token=='('):
        token=lex()
        condition()
        if(token!=')'):
            print("ERROR:Missing ')' in line "+str(line))
            print("Doublewhile conditions should be inside '(' and ')'")
            quit()
        token=lex()
    else:
        print("ERROR:Missing '(' in line "+str(line))
        print("Doublewhile conditions should be inside '(' and ')'")
        quit()
    statements()
    if(token=="else"):
        token=lex()
        statements()
    else:
        print("ERROR:Missing Doublewhile 'else' in line "+str(line))
        quit()

def loop_stat():#not implemented for intermidate and final code
    statements()

def exit_stat():#not implemented for intermidate and final code
    return

def forcase_stat():
    global line
    global token
    first_quad=nextquad()
    while(token=="when"):
        token=lex()
        if(token=='('):
            token=lex()
            (true_list,false_list)=condition()
            if(token==')'):
                token=lex()
                if(token==':'):
                    backpatch(true_list,nextquad())
                    token=lex()
                    statements()
                    genquad("jump","_","_",first_quad)
                    backpatch(false_list,nextquad())
                else:
                    print("ERROR:Missing ':' in line "+str(line))
                    print("When statements should look like this: when('condition'):'statements'")
                    quit()
            else:
                print("ERROR:Missing ')' in line "+str(line))
                print("When conditions should be inside '(' and ')'")
                quit()
        else:
            print("ERROR:Missing '(' in line "+str(line))
            print("When conditions should be inside '(' and ')'")
            quit()
    if(token=="default"):
        token=lex()
        if(token==':'):
            token=lex()
            statements()
        else:
            print("ERROR:Missing ':' in line "+str(line))
            print("Default When statements should look like this: default:'statements'")
            quit()
    else:
        print("ERROR:Needs a 'default' When case in line "+str(line))
        quit()

def incase_stat():#not implemented for intermidate and final code
    global line
    global token
    while(token=="when"):
        token=lex()
        if(token=='('):
            token=lex()
            condition()
            if(token==')'):
                token=lex()
                if(token==':'):
                    token=lex()
                    statements()
                else:
                    print("ERROR:Missing ':' in line "+str(line))
                    print("When statements should look like this: when('condition'):'statements'")
                    quit()
            else:
                print("ERROR:Missing ')' in line "+str(line))
                print("When conditions should be inside '(' and ')'")
                quit()
        else:
            print("ERROR:Missing '(' in line "+str(line))
            print("When conditions should be inside '(' and ')'")
            quit()

def call_stat():
    global token
    global pars
    global depth
    if(token in IDs):
        id=token
        try:
            (func_entity,entity_level)=searchFuncEntity(id)
            func_type=func_entity[1]
            arguments=func_entity[3]
        except:
            print("ERROR:Undeclared procedure in line "+str(line))
            quit()
        if(func_type!='proc'):
            print("ERROR:The 'call' statement can only be used for procedures in line "+str(line))
            quit()
            
        token=lex()
        actualpars()

        pars_length=len(pars)
        arguments_length=len(arguments)
        if(depth>=2):#this is useful for multiple function calls
                     #i.e. res:=max(in max(in x, in y), in max(in k, in l)))
            temp_pars_length=0
            for i in range(len(pars)):
                if(depth==pars[i][0]):
                    temp_pars_length+=1
            pars_length=temp_pars_length 
            if(pars_length>arguments_length):
                arguments_length+=1
            elif(pars_length<arguments_length):
                pars_length+=1 
        if(pars_length!=arguments_length):
            print("ERROR:Procedure arguments must match in line "+str(line))
            quit()
        for i in range(len(arguments)):
            if(pars[i][2]=='CV'):
                arg='in'
            elif(pars[i][2]=='REF'):
                arg='inout'
            if(arg!=arguments[i]):
                print("ERROR:Procedure arguments must match in line "+str(line))
                print("Found '"+arg+"' but '"+arguments[i]+"' was expected for procedure '"+id+"'") 
                quit()
        
        remaining_pars=[]
        for parameter in pars :#this is useful for multiple function calls
                                   #i.e. res:=max(in max(in x, in y), in max(in k, in l)))
            if(parameter[0]==depth):#only the currently called quads must be added
                genquad("par",parameter[1],parameter[2],"_")
            else:
                remaining_pars.append(parameter)
        pars=remaining_pars
        depth-=1
        genquad("call","_","_",id)
    else:
        print("ERROR:Needs a legitimate subprogram ID in line "+str(line))
        quit()
    

def return_stat():
    x=expression()
    genquad("retv",x,"_","_")
        

def input_stat():
    global token
    if(token=='('):
        token=lex()
        if(token in IDs):
            id=token
            token=lex()
            if(token!=')'):
                print("ERROR:Missing ')' in line "+str(line))
                print("Input statements should be inside '(' and ')'")
                quit()
            token=lex()
            genquad("inp",id,"_","_")
        else:
            print("ERROR:Undeclared Input ID in line "+str(line))
            quit()
    else:
        print("ERROR:Missing '(' in line "+str(line))
        print("Input statements should be inside '(' and ')'")
        quit()

def print_stat():
    global token
    if(token=='('):
        token=lex()
        expres=expression()
        if(token!=')'):
            print("ERROR:Missing ')' in line "+str(line))
            print("Print statements should be inside '(' and ')'")
            quit()
        token=lex()
        genquad("out",expres,"_","_")
    else:
        print("ERROR:Missing '(' in line "+str(line))
        print("Print statements should be inside '(' and ')'")
        quit()


#functions for Intermediate-Code
def nextquad():
    return num_quad;
    
def genquad(op,x,y,z):
    global num_quad
    newquad=[num_quad,op,x,y,z]
    quad_list.append(newquad)
    num_quad += 1;

def newTemp():
    global temp_num
    temp="T_"+str(temp_num)
    addNewTempEntity(temp)
    temp_num += 1
    return temp

def makeList(num_quad):
    new_list=[]
    new_list.append(num_quad)
    return new_list

def mergeList(list_1,list_2):
    merged_list=list_1+list_2
    return merged_list
    
def backpatch(backpatch_list,z):
    for quad in backpatch_list:
        quad_list[quad][4]=z


#the generated quads are written in the .int file
def createIntFile():
    intFile=open(filename+".int","w")
    for quad in final_quad_list:
        #+1 on quad[0] to match the asm labels
        intFile.write(str(quad[0]+1)+": "+str(quad[1])+" "+str(quad[2])+" "+str(quad[3])+" "+str(quad[4])+"\n")
    intFile.close()

#create the .c file
def createCFile():
    cFile=open(filename+".c","w")
    cFile.write("#include <stdio.h>\n")
    cFile.write("int main()\n{\n")
    num=len(IDs)
    if(num>0):
        cFile.write("\tint ")
        for i in range (0,num-1): #initialize the variables
            cFile.write(IDs[i]+",")
        cFile.write(IDs[num-1]+";\n")
    if(temp_num>0):
        cFile.write("\tint ")
        for j in range(0,temp_num-1): #initialize the temporary variables
            cFile.write("T_"+str(j)+",")
        cFile.write("T_"+str(temp_num-1)+";\n")
    for quad in final_quad_list: #iterate the quad_list and assign each quad to a c command
        line_num=str(quad[0])
        operator=str(quad[1])
        x=str(quad[2])
        y=str(quad[3])
        z=str(quad[4])
        if(operator==":="):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" "+z+"="+x+";")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator in ("+","-","*","/")):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" "+z+"="+x+operator+y+";")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator=="jump"):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" goto L_"+z+";")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator in ("=","<",">","<=",">=","<>")):
            cFile.write("\tL_"+line_num+":")
            if(operator=="<>"):
                cFile.write(" if("+x+"!="+y+")")
            elif(operator=="=="):
                cFile.write(" if("+x+"=="+y+")")
            else:
                cFile.write(" if("+x+operator+y+")")
            cFile.write(" goto L_"+z+";")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator=="retv"):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" return "+x+";")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator=="call"):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" "+z+"();")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator=="out"):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" printf(\"%d\","+x+");")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator=="inp"):
            cFile.write("\tL_"+line_num+":")
            cFile.write(" scanf(\"%d\",&"+x+");")
            cFile.write(" //("+operator+","+x+","+y+","+z+")")
            cFile.write("\n")
        elif(operator=="halt"):
            break;
    cFile.write("}")


#functions for Symbol Table
def addNewScope():
    global nested_level
    offset=12
    scopes.append([[nested_level,offset]])
    nested_level+=1
    printScopes("new scope")
    
def addNewVarEntity(var_name):
    offset=scopes[-1][0][1]
    scopes[-1].append([var_name,'var',offset])
    scopes[-1][0][1]+=4
    printScopes("new var")

def addNewParEntity(par_name,par_mode):
    offset=scopes[-1][0][1]
    if(par_mode=='in'):
        par_mode='CV'
    elif(par_mode=='inout'):
        par_mode='REF'
    scopes[-1].append([par_name,'par',par_mode,offset])
    scopes[-1][0][1]+=4
    printScopes("new par")

def addNewTempEntity(temp_name):
    offset=scopes[-1][0][1]
    scopes[-1].append([temp_name,'temp',offset])
    scopes[-1][0][1]+=4
    printScopes("new temp")

def addNewFuncEntity(func_name):
    if(func_flag==1):
        scopes[-2].append([func_name,'proc',[]])
    else:
        scopes[-2].append([func_name,'func',[]])
    printScopes("new func or proc")
    
def addNewArgument(func_name,par_mode):
    if(par_mode=='in'):
        argument='in'
    elif(par_mode=='inout'):
        argument='inout'
    (func_entity,entity_level)=searchFuncEntity(func_name)
    func_entity[2].append(argument)
    printScopes("new argument")

def searchFuncEntity(entity_name):#searching from last entity to first
    for scope in reversed(scopes):
        for entity in reversed(scope):
            etype=entity[1]
            if(entity[0]==entity_name and (etype=='func' or etype=='proc')):
                entity_level=scope[0][0]
                return entity,entity_level

def searchEntity(entity_name):#searching from last entity to first
    for scope in reversed(scopes):
        for entity in reversed(scope):
            etype=entity[1]
            if(entity[0]==entity_name and (etype!='func' or etype!='proc')):
                entity_level=scope[0][0]
                return entity,entity_level

def deleteScope():
    global nested_level
    nested_level-=1
    scopes.pop()
    printScopes("delete scope")

def printScopes(scope_func):
    if(print_scopes):
        n= len(scopes)
        print(scope_func)
        for i in range (n):
            print (scopes[i])
        print("\n")


#functions for Final-Code
def gnlvcode(index,v):
    try:
        (entity,entity_level)=searchEntity(v)
        etype=entity[1]
        offset=entity[-1]
    except:
        print("ERROR:Undeclared variable: "+str(v))
        quit()
    mips_command="lw\t\t$t0,\t-4($sp)"
    final_code_list[index].append(mips_command)
    n=nested_level-entity_level-1#distance between levels
    while(n>1):
        mips_command="lw\t\t$t0,\t-4($t0)"
        final_code_list[index].append(mips_command)
        n-=1
    mips_command="addi\t$t0,\t$t0,\t-"+str(offset)
    final_code_list[index].append(mips_command)

def loadvr(index,v,r):
    if(str(v).isdigit()):
        mips_command="li\t\t"+r+",\t"+str(v)
        final_code_list[index].append(mips_command)
    else:
        try:
            (entity,entity_level)=searchEntity(v)
            etype=entity[1]
            offset=entity[-1]
        except:
            print("ERROR:Undeclared variable: "+str(v))
            quit()
        if(entity_level==0 and etype=='var'):
            if(nested_level==1):#global variable in main level so it's a local varible
                mips_command="lw\t\t"+r+",\t-"+str(offset)+"($sp)"
                final_code_list[index].append(mips_command)
            else:#global variable in nested level 
                mips_command="lw\t\t"+r+",\t-"+str(offset)+"($s0)"
                final_code_list[index].append(mips_command)
        elif(entity_level==nested_level-1):#same level
            #local variable or in-parameter or temporary variable
            if(etype=='var' or (etype=='par' and entity[2]=='CV') or etype=='temp'):
                mips_command="lw\t\t"+r+",\t-"+str(offset)+"($sp)"
                final_code_list[index].append(mips_command)
            #inout-parameter
            elif(etype=='par' and entity[2]=='REF'):
                mips_command="lw\t\t"+r+",\t-"+str(offset)+"($sp)"
                final_code_list[index].append(mips_command)
                mips_command="lw\t\t"+r+",\t($t0)"
                final_code_list[index].append(mips_command)
            else:
                print("Must never reach here!")
                print("Unknown Error [1]")
                quit()
        elif(entity_level<nested_level-1):#different level
            name=entity[0]
            #local variable or in-parameter
            if(etype=='var' or (etype=='par' and entity[2]=='CV')):
                gnlvcode(index,name)
                mips_command="lw\t\t"+r+",\t($t0)"
                final_code_list[index].append(mips_command)
            #inout-parameter
            elif(etype=='par' and entity[2]=='REF'):
                gnlvcode(index,name)
                mips_command="lw\t\t$t0,\t($t0)"
                final_code_list[index].append(mips_command)
                mips_command="lw\t\t"+r+",\t($t0)"
                final_code_list[index].append(mips_command)
            else:
                print("Must never reach here!")
                print("Unknown Error [2]")
                quit()
        else:
            print("Must never reach here!")
            print("Unknown Error [3]")
            quit()

def storerv(index,r,v):
    try:
        (entity,entity_level)=searchEntity(v)
        offset=entity[-1]
        etype=entity[1]
    except:
        print("ERROR:Undeclared variable:"+str(v))
        quit()
    if(entity_level==0 and etype=='var'):
        if(nested_level-1==0):#global variable in main level so it's a local varible
            mips_command="sw\t\t"+r+",\t-"+str(offset)+"($sp)"
            final_code_list[index].append(mips_command)
        else:#global variable in nested level 
            mips_command="sw\t\t"+r+",\t-"+str(offset)+"($s0)"
            final_code_list[index].append(mips_command)
    elif(entity_level==nested_level-1):#same level
        #local variable or in-parameter or temporary variable
        if(etype=='var' or (etype=='par' and entity[2]=='CV') or etype=='temp'):
            mips_command="sw\t\t"+r+",\t-"+str(offset)+"($sp)"
            final_code_list[index].append(mips_command)
        #inout-parameter
        elif(etype=='par' and entity[2]=='REF'):
            mips_command="lw\t\t$t0,\t-"+str(offset)+"($sp)"
            final_code_list[index].append(mips_command)
            mips_command="sw\t\t"+r+",\t($t0)"
            final_code_list[index].append(mips_command)
        else:
            print("Must never reach here!")
            print("Unknown Error [4]")
            quit()
    elif(entity_level<nested_level-1):#different level
        name=entity[0]
        #variable or in-parameter
        if(etype=='var' or (etype=='par' and entity[2]=='CV')):
            gnlvcode(index,name)
            mips_command="sw\t\t"+r+",\t($t0)"
            final_code_list[index].append(mips_command)
            
        #inout-parameter
        elif(etype=='par' and entity[2]=='REF'):
            gnlvcode(index,name)
            mips_command="lw\t\t$t0,\t($t0)"
            final_code_list[index].append(mips_command)
            mips_command="sw\t\t"+r+",\t($t0)"
            final_code_list[index].append(mips_command)
        else:
            print("Must never reach here!")
            print("Unknown Error [5]")
            quit()
    else:
        print("Must never reach here!")
        print("Unknown Error [6]")
        quit()
     
def generateFinalCode(index,quad,block_name):
    global par_index
    num_quad=quad[0]
    op=quad[1]
    x=quad[2]
    y=quad[3]
    z=quad[4]
    
    relational_op=["=","<",">","<=",">=","<>"]
    branch=["beq","blt","bgt","ble","bge","bne"]#used for matching
    
    arop=["+","-","*","/"]
    asm_arop=["add","sub","mul","div"]#used for matching
    
    if(op=='jump'):
        mips_command="b\t\tL"+str(z+1)#z+1 because the quads start from 0
        final_code_list[index].append(mips_command)
    elif(op in relational_op):
        loadvr(index,x,'$t1')
        loadvr(index,y,'$t2')
        relop=branch[relational_op.index(op)]#matching
        mips_command=relop+"\t\t$t1,\t$t2,\tL"+str(z+1)
        final_code_list[index].append(mips_command)
    elif(op==':='):
        loadvr(index,x,'$t1')
        storerv(index,'$t1',z)
    elif(op in arop):
        loadvr(index,x,'$t1')
        loadvr(index,y,'$t2')
        asm_op=asm_arop[arop.index(op)]
        mips_command=asm_op+"\t\t$t1,\t$t1,\t$t2"
        final_code_list[index].append(mips_command)
        storerv(index,'$t1',z)
    elif(op=="out"):
        mips_command="li\t\t$v0,\t1"
        final_code_list[index].append(mips_command)
        loadvr(index,x,'$a0')
        mips_command="syscall"
        final_code_list[index].append(mips_command)
    elif(op=="inp"):
        mips_command="li\t\t$v0,\t5"
        final_code_list[index].append(mips_command)
        mips_command="syscall"
        final_code_list[index].append(mips_command)
        storerv(index,'$v0',x)
    elif(op=="retv"):
        try:
            (func_entity,func_level)=searchFuncEntity(block_name)
            func_type=func_entity[1]
        except:
            print("ERROR:Undeclared function: "+str(block_name))
            quit()
        if(func_type=='proc'):
            print("ERROR:Procedures cannot have a 'return' statement in line "+str(line))
            quit()
        returned[0][1]=1 #function returned
        loadvr(index,x,'$t1')
        mips_command="lw\t\t$t0,\t-8($sp)"
        final_code_list[index].append(mips_command)
        mips_command="sw\t\t$t1,\t($t0)"
        final_code_list[index].append(mips_command)
    elif(op=="par"):
        try:
            (entity,entity_level)=searchEntity(x)
            offset=entity[-1]
        except:
            print("ERROR:Undeclared variable: "+str(x))
            quit()
        if(program_name==block_name):
            framelength=scopes[-1][0][1]-4
            entity_level=0
        else:
            try:
                (func_entity,entity_level)=searchFuncEntity(block_name)
                framelength=func_entity[4]
            except:
                print("ERROR:Undeclared function/procedure: "+str(block_name))
                quit()
        if(y=="CV"):
            if(par_index==0):#for the first parameter only
                mips_command="addi\t$fp,\t$sp,\t"+str(framelength)
                final_code_list[index].append(mips_command)
            loadvr(index,x,'$t0')
            mips_command="sw\t\t$t0,\t-"+str(12+4*par_index)+"($fp)"
            final_code_list[index].append(mips_command)
            par_index+=1
        elif(y=="REF"):
            try:
                (entity,entity_level)=searchEntity(x)
                etype=entity[1]
                par_mode=entity[2]
                offset=entity[-1]
            except:
                print("ERROR:Undeclared variable:"+str(v))
                quit()
            if(par_index==0):#for the first parameter only
                mips_command="addi\t$fp,\t$sp,\t"+str(framelength)
                final_code_list[index].append(mips_command)
            if(entity_level==nested_level-1):#same level
                #local variable or in-parameter
                if(etype=="var" or(etype=="par" and par_mode=="CV")):
                    mips_command="addi\t$t0,\t$sp,\t-"+str(offset)
                    final_code_list[index].append(mips_command)
                    mips_command="sw\t\t$t0,\t-"+str(12+4*par_index)+"($fp)"
                    final_code_list[index].append(mips_command)
                #inout-parameter
                elif(etype=="par" and par_mode=="REF"):
                    mips_command="lw\t\t$t0,\t-"+str(offset)+"($sp)"
                    final_code_list[index].append(mips_command)
                    mips_command="sw\t\t$t0,\t-"+str(12+4*par_index)+"($fp)"
                    final_code_list[index].append(mips_command)
                else:
                    print("Must never reach here!")
                    print("Unknown Error [7]")
                    quit()
                par_index+=1
            else:
                if(etype=="var" or(etype=="par" and par_mode=="CV")):
                    gnlvcode(index,x)
                    mips_command="sw\t\t$t0,\t-"+str(12+4*par_index)+"($fp)"
                    final_code_list[index].append(mips_command)
                elif(etype=="par" and par_mode=="REF"):
                    gnlvcode(index,x)
                    mips_command="lw\t\t$t0,\t($t0)"
                    final_code_list[index].append(mips_command)
                    mips_command="sw\t\t$t0,\t-"+str(12+4*par_index)+"($fp)"
                    final_code_list[index].append(mips_command)
                else:
                    print("Must never reach here!")
                    print("Unknown Error [8]")
                    quit()
                par_index+=1
        elif(y=="RET"):
            if(par_index==0):#framelength-4 because symbol table's offset is always +4
                if(block_name!=program_name):
                    framelength-=4
                mips_command="addi\t$fp,\t$sp,\t"+str(framelength)
                final_code_list[index].append(mips_command)
            par_index=0
            mips_command="addi\t$t0,\t$sp,\t-"+str(offset)
            final_code_list[index].append(mips_command)
            mips_command="sw\t\t$t0,\t-8($fp)"
            final_code_list[index].append(mips_command)
        else:
            print("Must never reach here!")
            print("Unknown Error [9]")
            quit()
    elif(op=="call"):
        par_index=0
        callee_framelength=0
        try:
            (callee,callee_level)=searchFuncEntity(z)
            etype=callee[1]
            num_quad=callee[2]
            callee_framelength=callee[-1]
        except:
            print("ERROR::Undeclared function/procedure:"+str(z))
            quit()
        try:
            if(program_name==block_name):#main is caller
                caller="main"
                main_framelength=scopes[-1][0][1]
                callee_framelength=main_framelength-4
                caller_level=-1
            else:#caller is another func
                (caller,caller_level)=searchFuncEntity(block_name)
                mips_command="addi\t$fp,\t$sp,\t"+str(callee_framelength)
                final_code_list[index].append(mips_command)
        except:
            print("ERROR::Undeclared function/procedure:"+str(block_name))
            quit()        
        if(callee_level==caller_level):
            mips_command="lw\t\t$t0,\t-4($sp)"
            final_code_list[index].append(mips_command)
            mips_command="sw\t\t$t0,\t-4($fp)"
            final_code_list[index].append(mips_command)
        else:
            mips_command="sw\t\t$sp,\t-4($fp)"
            final_code_list[index].append(mips_command)        
        mips_command="addi\t$sp,\t$sp,\t"+str(callee_framelength)
        final_code_list[index].append(mips_command)
        mips_command="jal\t\tL"+str(num_quad)
        final_code_list[index].append(mips_command)
        mips_command="addi\t$sp,\t$sp,\t-"+str(callee_framelength)
        final_code_list[index].append(mips_command)
    elif(op=="begin_block"):
        offset=scopes[-1][0][1]
        if(block_name==program_name):
            asmFile=open(filename+".asm","a")#write the main label
            asmFile.write("\nLmain:")
            mips_command="addi\t$sp,\t$sp,\t"+str(offset)
            final_code_list[index].append(mips_command)
            mips_command="move\t$s0,\t$sp"
            final_code_list[index].append(mips_command)
        else:
            mips_command="sw\t\t$ra,\t-0($sp)"
            final_code_list[index].append(mips_command)
    elif(op=="end_block"):
        if(block_name!=program_name):
            mips_command="lw\t\t$ra,\t-0($sp)"
            final_code_list[index].append(mips_command)
            mips_command="jr\t\t$ra"
            final_code_list[index].append(mips_command)
    elif(op=="halt"):
        mips_command="li\t\t$v0,\t10"
        final_code_list[index].append(mips_command)
        mips_command="syscall"
        final_code_list[index].append(mips_command)
    else:
        print("Unknown quad: "+str(op))
        print("Exiting program...")
        quit()
        
def fillFinalCodeList(block_name):
    global quad_list
    for quad in quad_list:#for every quad of the last block generate asm-code
        index=quad[0]
        generateFinalCode(index,quad,block_name)
        final_code_list.append([])
        final_quad_list.append(quad)
    quad_list=[]
    fillAsmFile()

def fillAsmFile():
    global helper
    asmFile=open(filename+".asm","a")
    n = len(final_code_list)
    i=helper#to keep track of which asm code has been written
    while i < n-1:        
        k = len(final_code_list[i])
        asmFile.write("\nL"+str(i+1)+":")
        for j in range (k):
            asmFile.write("\r\t"+final_code_list[i][j])
        i+=1
    asmFile.close()
    helper=n-1

def writeAssemblyFirstLine():
    asmFile=open(filename+".asm","w")
    asmFile.write("L0:\r\tb\t\tLmain")


#handles the input file
def open_file(file):
    split=file.split('.')
    if len(split)==2:
        if split[1] == "min":
            return open(file, 'r')
        else:
            print("ERROR:Not a Minimal++ file")
            quit()
    else:
        print("ERROR:Something wrong with file")
        quit()


#global variables for the Lex-Synt Analysis
line=1
token=''

#global variables for the Intermidate-Code
num_quad=0
quad_list=[]
temp_num=0
program_name=''

pars=[] #this is useful for nested function calls
depth=0 #this is useful for nested function calls

#global variables for Symbol Table
scopes=[]
nested_level=0
func_flag=0

#print_scopes=True
print_scopes=False

#global variables for Final-Code
final_quad_list=[]
final_code_list=[[]]
par_index=0
helper=0#useful for writing the asm file
returned=[]#to make sure that a 'function' returns
                         
#user enters their file and program() does the rest of the analysis
filename=raw_input("Please enter a file to analyse: ")
#filename=sys.argv[1]
f=open_file(filename)
filename=filename.split('.')[0] #name the generated files like the given file

writeAssemblyFirstLine()

token=lex()
program()
print("Successful Analysis")

createIntFile()
print("Intermediate-Code File Created")

createCFile()
print("C-Code File Created")

print("Assembly-Code File Created")

