# This will recursively remove all the temp files generated by NEURON, JNML, and /tests/runsuite.py from the NeuroML2 folder

find . -type f -name '*.hoc' -delete
find . -type f -name '*.dat' -delete
find . -type f -name '*.mod' -delete
find . -type f -name '*_nrn.py' -delete
find . -type f -name '*_TestBed.xml' -delete
find . -type f -name 'PartialBulb*.nml' -delete

find . -type d -name "x86_64" -exec rm -Rf {} +