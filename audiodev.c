/*
 * Copyright (c) 2014 David Jander
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <alsa/asoundlib.h>
#include <math.h>
#include <string.h>
#include <sys/poll.h>
#include "audiodev.h"

#define PERIODSIZE 128

#define MICROSTEPS 16
#define STEP_PERIOD_SIZE (4 * MICROSTEPS)
#define CURR_OFFSET 0.0
#define CURR_AMPLITUDE 30000.0
#define AMPLITUDE_DC_DEFAULT 0.6 /* Amplitude multiplier for constant current */

static snd_pcm_t *playback_handle = NULL;
static unsigned int dim = 0;
static double currents[MAX_DIM * 2];
static double position[MAX_DIM];
static double origin[MAX_DIM];
static double destination[MAX_DIM];
static double incvec[MAX_DIM];
static double amp[MAX_DIM];
static int16_t buf[PERIODSIZE * MAX_DIM * 4]; /* Make buf hold twice a period */
unsigned int buf_idx = 0;
static double tim;
static double dist;
static double delta_t;
static double feedrate = 0.33;
static double feedrate_begin = 0.05;
static double feedrate_end = 0.05;
static double amplitude_dc = AMPLITUDE_DC_DEFAULT;

double sintab[STEP_PERIOD_SIZE], costab[STEP_PERIOD_SIZE];
int angle[MAX_DIM];
double speed[MAX_DIM];

static void vec_clear(double *v)
{
	int i;
	for(i = 0; i < MAX_DIM; i ++) {
		v[i] = 0.0;
	}
}

static void vec_copy(double *dst, double *src)
{
	int i;
	for(i = 0; i < MAX_DIM; i ++) {
		dst[i] = src[i];
	}
}

static void vec_diff(double *res, double *v1, double *v2)
{
	int i;
	for(i = 0; i < MAX_DIM; i ++) {
		res[i] = v1[i] - v2[i];
	}
}

static void vec_sum(double *res, double *v1, double *v2)
{
	int i;
	for(i = 0; i < MAX_DIM; i ++) {
		res[i] = v1[i] + v2[i];
	}
}

static void vec_mul_scalar(double *res, double *v, double fact)
{
	int i;
	for(i = 0; i < MAX_DIM; i ++) {
		res[i] = v[i] * fact;
	}
}

static double vec_sum_squares(double *v)
{
	int i;
	double res = 0.0;
	for(i = 0; i < MAX_DIM; i ++) {
		res += v[i] * v[i];
	}
	return res;
}

static double vec_dist(double *v1, double *v2)
{
	double d[MAX_DIM];
	double sqd;

	vec_diff(d, v1, v2);
	sqd = vec_sum_squares(d);
	return sqrt(sqd);
}

int audiostep_open(const char *devname, int channels, unsigned int rate)
{
	int err;
	snd_pcm_hw_params_t *hw_params;
	int dir = 0;
	int i;
	snd_pcm_uframes_t periods = PERIODSIZE;
	snd_pcm_uframes_t bufsize = PERIODSIZE * 4;

	dim = channels;

	if ((err = snd_pcm_open (&playback_handle, devname, SND_PCM_STREAM_PLAYBACK, 0)) < 0) {
		fprintf(stderr, "cannot open audio device %s (%s)\n", devname, snd_strerror(err));
		return err;
	}

	if ((err = snd_pcm_hw_params_malloc (&hw_params)) < 0) {
		fprintf(stderr, "cannot allocate hardware parameter structure (%s)\n", snd_strerror (err));
		return err;
	}

	if ((err = snd_pcm_hw_params_any (playback_handle, hw_params)) < 0) {
		fprintf(stderr, "cannot initialize hardware parameter structure (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params_set_access (playback_handle, hw_params, SND_PCM_ACCESS_RW_INTERLEAVED)) < 0) {
		fprintf(stderr, "cannot set access type (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params_set_format (playback_handle, hw_params, SND_PCM_FORMAT_S16_LE)) < 0) {
		fprintf(stderr, "cannot set sample format (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params_set_rate_near (playback_handle, hw_params, &rate, &dir)) < 0) {
		fprintf(stderr, "cannot set sample rate (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params_set_channels (playback_handle, hw_params, 2 * channels)) < 0) {
		fprintf(stderr, "cannot set channel count (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params_set_buffer_size_near(playback_handle, hw_params, &bufsize)) < 0) {
		fprintf(stderr, "cannot set buffer size (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params_set_period_size_near(playback_handle, hw_params, &periods, &dir)) < 0) {
		fprintf(stderr, "cannot set period size (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_hw_params (playback_handle, hw_params)) < 0) {
		fprintf(stderr, "cannot set parameters (%s)\n", snd_strerror (err));
		goto out_free;
	}

	if ((err = snd_pcm_prepare (playback_handle)) < 0) {
		fprintf(stderr, "cannot prepare audio interface for use (%s)\n", snd_strerror (err));
		goto out_free;
		exit(1);
	}

	vec_clear(position);
	vec_clear(speed);
	vec_clear(destination);
	vec_clear(origin);
	vec_clear(amp);
	for (i = 0; i < MAX_DIM * 2; i ++) {
		currents[i] = 0.0;
	}

	for(i = 0; i < STEP_PERIOD_SIZE; i ++) {
		sintab[i] = CURR_OFFSET + CURR_AMPLITUDE * sin((i * 2 * M_PI) / (double)STEP_PERIOD_SIZE);
		costab[i] = CURR_OFFSET + CURR_AMPLITUDE * cos((i * 2 * M_PI) / (double)STEP_PERIOD_SIZE);
	}

out_free:
	snd_pcm_hw_params_free(hw_params);
	return err;
}

static void calc_amplitude(void)
{
	int i;

	for(i = 0; i < MAX_DIM; i++) {
		amp[i] = amplitude_dc + fabs(incvec[i]) * delta_t * 10.0;
		if (amp[i] > 1.0)
			amp[i] = 1.0;
	}
}

void set_destination(double *v)
{
	int i;
	double dif[MAX_DIM];
	vec_copy(origin, position);
	vec_copy(destination, v);
	tim = 0.0;
	delta_t = feedrate_begin;
	dist = vec_dist(position, v);
	if(dist == 0.0) {
		vec_clear(incvec);
		for(i = 0; i < MAX_DIM; i++)
			amp[i] = amplitude_dc;
		return;
	}
	vec_diff(dif, v, origin);
	for(i = 0; i < MAX_DIM; i++)
		incvec[i] = dif[i] / dist;
	calc_amplitude();
}

void next_position(int *steps)
{
	double newp[MAX_DIM];
	double err[MAX_DIM];
	int i;

	tim += 1.0;
	vec_mul_scalar(newp, incvec, tim);
	vec_sum(newp, newp, origin);
	vec_diff(err, newp, position);
	for (i = 0; i < MAX_DIM; i++) {
		steps[i] = (int)err[i];
		position[i] += (double)steps[i];
	}
}

void pos_iteration(int *steps)
{
	double dtinc = 0.0005;
	double dt;

	next_position(steps);
	dt = dist - tim;
	if ((((delta_t - feedrate_end) / dtinc) >= dt) && (delta_t > feedrate_end))
		delta_t -= dtinc;
	else if (delta_t < (feedrate - dtinc))
		delta_t += dtinc;
}

void set_speed(double *speed)
{
	/* TODO */
}

static int write_current_reps(double *c, int reps)
{
	int i, t;
	int ret = 0, err;

	//printf("write_current_reps reps = %d, delta_t = %lf\n", reps, delta_t);
	for(t = 0; t < reps; t++) {
		for(i = 0; i < (dim * 2); i++) {
			buf[buf_idx + i] = (int16_t)c[i];
		}
		if (buf_idx < (sizeof(buf) - dim * 2))
			buf_idx += dim * 2;
		if(buf_idx >= (PERIODSIZE * dim * 2)) {
			if ((err = snd_pcm_writei(playback_handle, buf, PERIODSIZE)) != PERIODSIZE) {
				fprintf(stderr, "write to audio interface failed (%s)\n", snd_strerror (err));
				snd_pcm_prepare(playback_handle);
			} else {
				ret += err;
				buf_idx -= (PERIODSIZE * dim * 2);
			}
			//printf("Wrote %d periods\n", err);
		}
	}
	return ret;
}

static void motor_do_steps(int i, int s, double *vl, double *vr)
{
	angle[i] += s;
	if (angle[i] >= STEP_PERIOD_SIZE)
		angle[i] -= STEP_PERIOD_SIZE;
	else if (angle[i] < 0)
		angle[i] += STEP_PERIOD_SIZE;

	/* TODO: X-fade to square wave for high-speed */

	*vl = sintab[angle[i]] * amp[i];
	*vr = costab[angle[i]] * amp[i];
}

/* Returns:
 * -1 if destination reached, or
 * number of frames written to audio device, or
 * < -1 in case of error. (-EPERM == -1 cannot be returned)
 */
int main_iteration(void)
{
	int i;
	int steps[MAX_DIM];
	int reps;
	double repsf;
	static double repserr = 0.0;
	int written;

	if (tim >= dist)
		return -1;

	pos_iteration(steps);
	calc_amplitude();
	for (i = 0; i < MAX_DIM; i ++) {
		motor_do_steps(i, steps[i], &currents[i * 2], &currents[i * 2 + 1]);
	}
	repsf = (1.0 / delta_t) + repserr;
	reps = (int)repsf;
	repserr = (double)reps - repsf;
	written = write_current_reps(currents, reps);
	return written;
}

/* Oversimplistic fileno() implementation assuming there's only one file-
 * descriptor involved. Should be the case anyway */
int audio_fileno(void)
{
	struct pollfd pfd;

	snd_pcm_poll_descriptors(playback_handle, &pfd, 1);

	return pfd.fd;
}

void process_one_move(void)
{
	for (;;) {
		if (main_iteration() < 0)
			break;
	}
}

int push_more_audio_data(void)
{
	int ret = 0;

	for (;;) {
		ret = main_iteration();
		if (ret) /* Wrote data or error ? */
			return ret;
	}
	return ret; /* Never reached */
}

void zero_output(void)
{
	int i, err;

	memset(buf, 0, sizeof(buf));
	for(i = 0; i < 4; i ++) {
		if ((err = snd_pcm_writei(playback_handle, buf, PERIODSIZE)) != PERIODSIZE) {
			fprintf(stderr, "write to audio interface failed (%s)\n", snd_strerror (err));
			return;
		}
	}
	buf_idx = 0;
}

void set_constant_level(double *c)
{
	write_current_reps(c, 100);
}

void close_audio(void)
{
	snd_pcm_drain(playback_handle);
	snd_pcm_close(playback_handle);
}

void set_feedrate(double begin, double high, double end)
{
	// printf("set_feedrate: low=%f high=%f\n", low, high);
	feedrate = high;
	feedrate_begin = begin;
	feedrate_end = end;
}

void stop_audio(void)
{
	snd_pcm_drop(playback_handle);
}

void cancel_destination(void)
{
	tim = dist; /* Do as if we reached our destination */
}

void restart_audio(void)
{
	snd_pcm_prepare(playback_handle);
}

double *get_position(void)
{
	return position;
}

void set_position(double *v)
{
	vec_copy(position, v);
}

void set_amplitude_dc(double amp)
{
	amplitude_dc = amp;
}
