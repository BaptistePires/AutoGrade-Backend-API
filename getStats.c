#include<stdio.h>
#include<stdlib.h>
#include<sys/time.h>
#include<sys/times.h>
#include<sys/resource.h>
#include<unistd.h>
#include<string.h>
#define TICK ((double)sysconf(_SC_CLK_TCK))

struct timeval tv1;
struct timeval tv2;
struct tms tm1;
struct tms tm2;

void timeState(char *c);
void dump(char *command);


int main(int argc, char *argv[]){
	if(argc < 2){
		printf("Too few arguments, end of the programs\n");
		exit(EXIT_FAILURE);
	}
	char command[512] = "";
	for(int i = 1 ; i < argc ; i++){
		strcat(command,argv[i]);
		strcat(command," ");
	}
	printf("%s\n",command);
	for(int i = 0 ; i < 5 ; i++){
		timeState(command);
	}
	return 0;
}

void timeState(char *c){
	//gettimeofday(&tv1,NULL);
        //dump(c[1]);
        //gettimeofday(&tv2,NULL);
        //double long usec = tv2.tv_sec / 0.000001;
        //usec = (usec - (tv1.tv_sec / 0.000001)) + (tv2.tv_usec-tv1.tv_usec);
        //printf("temps d'execution => %Lf µsec \n\n",usec);
        double deb = times(&tm1);
        dump(c);
        double fin = times(&tm2);
        //printf("\nStatistiques de %s\n",c[0]);
        printf("{CpuTime : %f\n",(fin-deb)/TICK);
        //printf("Temps utilisateur : %Lf\n",(double long)(tm2.tms_utime-tm1.tms_utime)/TICK);
        //printf("Temps systeme : %Lf\n",(long double)(tm2.tms_stime-tm1.tms_stime)/TICK);
        //printf("Temps util. fils : %Lf\n",(long double)(tm2.tms_cutime-tm1.tms_cutime)/TICK);
	//printf("Temps sys. fils : %Lf\n",(long double)(tm2.tms_cstime-tm1.tms_cstime)/TICK);
}

void dump(char *command){
        if(system(command) == -1){
                printf("Erreur, processus impossible à créer\n");
               	exit(1);
        }
}

