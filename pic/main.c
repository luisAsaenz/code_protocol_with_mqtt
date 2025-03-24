#include "mcc_generated_files/system/system.h"

uint16_t ms=0;
uint16_t sec=0;

void timer_callback(void)
{
    ms++;
    if (ms>1000) 
    {
        ms -= 1000;
        sec++;
        IO_RA2_Toggle();
    }
}

void eusart_callback(void)
{
//    ms++;
}

uint8_t send_message(char * my_message){
    printf("%s",my_message);
    return 1;
}
        

#define BUFSIZE 4
#define MSGSIZE 64
#define TEAMSIZE 4
#define MSGTESTSIZE 64
#define MSGTESTCHAR 0

const char my_id='b';
const char team_ids[TEAMSIZE+1]="abcd";
char buffer_in[BUFSIZE+1];
char message_in[MSGSIZE+1];
char message_out[MSGSIZE+1];

//char stream_in[]="-----AZcb34567890YB-----------AZcd34567890YB--AZed34567890YB--AZdz34567890YB---AZed1234567890123456789012345678901234567890123456789012345678YB-";
//char read_char(void){
//    static int ii=0;
//    char c = stream_in[ii];
//    ii++;
//    if (ii>=(sizeof stream_in)-1)
//    {ii=0;}
//    return c;
//}

void fill_string(char * mystring,char value,unsigned int size){
    for (int ii=0;ii<size;ii++){
        mystring[ii]=value;
    }
}

unsigned int find_char(char * mystring, char value,unsigned int size){
    char c=0;
    for (int ii=0;ii<size;ii++){
        c= mystring[ii];
//        printf("%c,%c;",value,mystring[ii]);
        if (c==value){
            return 1;
        }
    }
    return 0;
}

void handle_message(unsigned int ii){
    message_in[ii-2]=0;
    printf("AZbaPIC: handling: %sYB",message_in+4);
}


int main(void)
{

    char c=0;
    unsigned int buffer_ii=0;
    unsigned int buffer_last_ii = 0;
    unsigned int message_ii=0;
    unsigned int message_last_ii=0;
    buffer_in[BUFSIZE]=0;
    message_in[MSGSIZE]=0;
    unsigned int message_incoming=0;
    fill_string(buffer_in,'a',BUFSIZE);
    fill_string(message_in,'_',MSGSIZE);
    message_in[MSGTESTSIZE]=MSGTESTCHAR;

    uint16_t ms_last=0;
    uint16_t sec_last=0;
    SYSTEM_Initialize();
    // If using interrupts in PIC18 High/Low Priority Mode you need to enable the Global High and Low Interrupts 
    // If using interrupts in PIC Mid-Range Compatibility Mode you need to enable the Global and Peripheral Interrupts 
    // Use the following macros to: 

    // Enable the Global Interrupts 
    INTERRUPT_GlobalInterruptEnable(); 

    // Disable the Global Interrupts 
    //INTERRUPT_GlobalInterruptDisable(); 

    // Enable the Peripheral Interrupts 
    INTERRUPT_PeripheralInterruptEnable(); 

    // Disable the Peripheral Interrupts 
    //INTERRUPT_PeripheralInterruptDisable(); 
    TMR1_Initialize();
    TMR1_Start();
    TMR1_TMRInterruptEnable();

    TMR1_OverflowCallbackRegister(timer_callback);

    EUSART1_Initialize();
    EUSART1_Enable();
//    EUSART1_TransmitEnable();
//    EUSART1_ReceiveEnable();
//    EUSART1_TransmitInterruptEnable();
//    EUSART1_ReceiveInterruptEnable();
//    
    EUSART1_RxCompleteCallbackRegister(eusart_callback);



//    printf("%lu", sizeof buffer_in);
    while(1)
    {
        if(EUSART1_IsRxReady())
        {
            c= EUSART1_Read();
//            printf("%c,%u,%u,%u,%u",c,buffer_last_ii,buffer_ii,message_ii,message_incoming);
            buffer_in[buffer_ii]=c;
            if (buffer_in[buffer_last_ii]=='A' & buffer_in[buffer_ii]=='Z'){
                printf("AZbaPIC: message startYB");
                fill_string(message_in,'_',MSGSIZE);
                message_in[MSGTESTSIZE]=MSGTESTCHAR;
                message_incoming=1;
                message_in[0] = buffer_in[buffer_last_ii];
                message_ii=1;
            }
            if (buffer_in[buffer_last_ii]=='Y' & buffer_in[buffer_ii]=='B'){
                printf("AZbaPIC: message endYB");
                message_incoming=0;
                message_in[message_ii] = buffer_in[buffer_ii];
                message_last_ii= message_ii;
                message_ii = message_ii+1;
                handle_message(message_ii);
            }
            if (message_incoming!=0){
                message_in[message_ii] = buffer_in[buffer_ii];

                if (message_ii==2){
                    unsigned result = 0;
                    char d=0;
                    d = message_in[message_ii];
                    result= find_char(team_ids,d,TEAMSIZE);
                    if (result==0){
                        printf("AZbaPIC: sender not in teamYB");
                    } else {
                        printf("AZbaPIC: sender in teamYB");
                    }
                }

                if (message_ii==3){
                    unsigned result = 0;
                    char d=0;
                    d = message_in[message_ii];
                    result= find_char(team_ids,d,TEAMSIZE);
                    if (result==0){
                        printf("AZbaPIC: receiver not in teamYB");
                    } else {
                        printf("AZbaPIC: receiver in teamYB");
                    }
                }

                message_last_ii= message_ii;
                message_ii = message_ii+1;
                if (message_ii<MSGTESTSIZE){} else{
                    printf("AZbaPIC: message too large. deletingYB");
                    message_incoming=0;
                    message_ii=0;
                }
            }
            buffer_last_ii= buffer_ii;
            buffer_ii = (buffer_ii+1)%BUFSIZE;

//            printf("%s,%s",buffer_in,message_in);
        }

//        if ((sec%3==0) & (sec!=sec_last)){
//            sprintf(message_out,"AZbaPIC: Heartbeat %u YB",sec);
//            send_message(message_out);
////            printf("AZbaPIC: Heartbeat %u YB",sec);
//        }
        
        if (IO_RC2_GetValue()!=0)
        {return 1;}
        
        sec_last = sec;
        ms_last = ms;
        
    }
}