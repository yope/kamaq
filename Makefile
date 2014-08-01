

all:
	python setup.py build_ext --inplace

clean:
	rm -f stepper.c stepper.so stepper.o
