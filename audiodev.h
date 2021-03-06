#ifndef __AUDIOSTEP_H__
#define __AUDIOSTEP_H__

#define MAX_DIM 4

int audiostep_open(const char *devname, int channels, unsigned int rate);
void set_destination(double *v);
int main_iteration(void);
void process_one_move(void);
void zero_output(void);
void close_audio(void);
void set_feedrate(double begin, double high, double end);
void set_constant_level(double *c);
int audio_fileno(void);
int push_more_audio_data(void);
void stop_audio(void);
void restart_audio(void);
void cancel_destination(void);
double *get_position(void);
void set_position(double *v);
void set_amplitude_dc(double amp);

#endif
