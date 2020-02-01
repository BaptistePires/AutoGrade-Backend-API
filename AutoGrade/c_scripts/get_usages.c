#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <string.h>
#include <sys/wait.h>

char *RESPONSE_TIMES_OUTPUT = "{\"status\": %d, \"data\": {\"cpu_time\": %ld}}\n";
char *RESPONSE_ERROR = "{\"status\": %d, \"error\":%S }\n";
char *STR_TIMES_OUTPUT = "{\"cpu_time\": %ld}";
char *PYTHON_PATH = "/usr/bin/python";
char *JAVA_PATH = "/usr/bin/java";
long ONE_BILLION = 10000000L;

/*
    This program is used to retrieve program statistics and return it as JSON.
    Argmuents must be : 
        - 0 : Current program name.
        - 1 : Langage (Currently only it only supports "python" and "java")
        - 2 : target program (full path)
        - 3..n : All the arguments you need to send to the target program.

    This program wont do any check on inputs. You must verify them before calling it.
*/

int main(int argc, char **argv){
    if (argc <= 3){
        printf(RESPONSE_ERROR, -1, "\"Not enought args\"");
        return -1;
    }

    pid_t pid;

    // Child that will execute the program
    if ((pid = fork()) == 0){

        int i;
        // Creating array of arguments (-2 is here to avoid args 0 and 1);
        // Looks like : [langage exec, target program, arg1,...,argN, NULL]
        char *argArray[argc];
        for (i = 2; i < argc; i++){
            argArray[i - 1] = argv[i];
        }
        argArray[i - 1] = NULL;

        if (strcmp(argv[1], "python") == 0){
            argArray[0] = PYTHON_PATH;
            execvp(argArray[0], argArray);
        }
        else if (strcmp(argv[1], "java") == 0){
            argArray[0] = JAVA_PATH;
            execvp(argArray[0], argArray);
        }
        else{
            //printf(RESPONSE_ERROR, -1, "Langage not supported.");
            exit(-1);
        }

        exit(0);
    }
    else
    {
        struct rusage usage;
        int status;
        // Wait for child process to end.
        wait4(pid, &status, 0, &usage);
        if (status == 0){
            // Full printed reponse. Will contains output_values + the status.
            // Get the time the program used.
            long totalSystemTime = usage.ru_stime.tv_usec + usage.ru_stime.tv_sec * ONE_BILLION;
            long totalUserTime = usage.ru_utime.tv_usec + usage.ru_utime.tv_sec * ONE_BILLION;

            // Buffer that will contains the reponse send to stdout.
            char fullJsonOutput[sizeof(RESPONSE_TIMES_OUTPUT) + sizeof(long)];
            sprintf(fullJsonOutput, RESPONSE_TIMES_OUTPUT, 0, totalUserTime + totalSystemTime);
            printf("%s\n", fullJsonOutput);
        }
        else{
            // If we were not able to retrieve times.
            printf(RESPONSE_ERROR, -1, "Error while retrieving usage times.");
        }
    }

    return 0;
}