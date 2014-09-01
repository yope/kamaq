#ifndef __AUDIOSTEP_H__
#define __AUDIOSTEP_H__

#define MAX_DIM 4

int audiostep_open(const char *devname, int channels, unsigned int rate);
void set_destination(double *v);
int main_iteration(void);
void process_one_move(void);
void zero_output(void);
void close_audio(void);
void set_feedrate(double rate);
void set_constant_level(double *c);
int audio_fileno(void);
int push_more_audio_data(void);

#endif
